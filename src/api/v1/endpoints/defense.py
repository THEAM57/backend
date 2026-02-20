from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.container import get_defense_service
from src.core.dependencies import get_current_user, require_teacher
from src.model.models import User
from src.schema.defense import (
    DefenseDayCreate,
    DefenseDayFull,
    DefenseDayListItem,
    DefenseDayListResponse,
    DefenseRegistrationCreate,
    DefenseRegistrationFull,
    DefenseSlotCreate,
    DefenseSlotFull,
    DefenseSlotListItem,
    DefenseSlotListResponse,
    MyDefenseItem,
    MyDefenseListResponse,
    ProjectTypeCreate,
    ProjectTypeFull,
    ProjectTypeInfo,
    ProjectTypeListResponse,
    ScheduledDefenseItem,
    ScheduledDefenseListResponse,
)
from src.services.defense_service import DefenseService


defense_router = APIRouter(prefix="/defense", tags=["defense"])


# --- Типы проектов ---


@defense_router.get("/project-types", response_model=ProjectTypeListResponse)
async def list_project_types(
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(get_current_user),
) -> ProjectTypeListResponse:
    """Получить список всех типов проектов."""
    types = await defense_service.get_all_project_types()
    items = [ProjectTypeFull.model_validate(t) for t in types]
    return ProjectTypeListResponse(items=items)


@defense_router.post("/project-types", response_model=ProjectTypeFull)
async def create_project_type(
    type_data: ProjectTypeCreate,
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(require_teacher),
) -> ProjectTypeFull:
    """Создать новый тип проекта (только преподаватель)."""
    try:
        project_type = await defense_service.create_project_type(type_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ProjectTypeFull.model_validate(project_type)


# --- Дни защит ---


@defense_router.get("/days", response_model=DefenseDayListResponse)
async def list_defense_days(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество дней на странице"),
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(get_current_user),
) -> DefenseDayListResponse:
    """Получить список дней защит с пагинацией."""
    days, total = await defense_service.get_days_paginated(page=page, limit=limit)
    items = [DefenseDayListItem.model_validate(d) for d in days]
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    return DefenseDayListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@defense_router.get("/days/{day_id}", response_model=DefenseDayFull)
async def get_defense_day(
    day_id: int,
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(get_current_user),
) -> DefenseDayFull:
    """Получить день защит по ID."""
    day = await defense_service.get_day_by_id(day_id)
    if not day:
        raise HTTPException(status_code=404, detail="Defense day not found")
    return DefenseDayFull.model_validate(day)


@defense_router.post("/days", response_model=DefenseDayFull)
async def create_defense_day(
    day_data: DefenseDayCreate,
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(require_teacher),
) -> DefenseDayFull:
    """Создать день защит (только преподаватель)."""
    day = await defense_service.create_day(day_data)
    return DefenseDayFull.model_validate(day)


# --- Слоты (время по дню + номер слота) ---


@defense_router.get("/slots", response_model=DefenseSlotListResponse)
async def list_defense_slots(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество слотов на странице"),
    date: date | None = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
    project_type_id: int | None = Query(None, description="Фильтр по ID типа проекта"),
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(get_current_user),
) -> DefenseSlotListResponse:
    """Получить список доступных слотов защит (слоты, на которые ещё никто не записан)."""
    slots, total = await defense_service.get_slots_paginated(
        page=page,
        limit=limit,
        filter_date=date,
        filter_project_type_id=project_type_id,
    )
    items = [DefenseSlotListItem.model_validate(slot) for slot in slots]

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    return DefenseSlotListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@defense_router.get("/scheduled", response_model=ScheduledDefenseListResponse)
async def list_scheduled_defenses(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество на странице"),
    date: date | None = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
    project_type_id: int | None = Query(None, description="Фильтр по ID типа проекта"),
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(get_current_user),
) -> ScheduledDefenseListResponse:
    """Получить список запланированных защит."""
    rows, total = await defense_service.get_scheduled_defenses_paginated(
        page=page,
        limit=limit,
        filter_date=date,
        filter_project_type_id=project_type_id,
    )
    items = []
    for slot, registrations_count in rows:
        setattr(slot, "registrations_count", registrations_count)
        items.append(ScheduledDefenseItem.model_validate(slot))
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    return ScheduledDefenseListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@defense_router.get("/slots/{slot_id}", response_model=DefenseSlotFull)
async def get_defense_slot(
    slot_id: int,
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(get_current_user),
) -> DefenseSlotFull:
    """Получить слот защиты по ID."""
    slot = await defense_service.get_slot_by_id(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Defense slot not found")
    return DefenseSlotFull.model_validate(slot)


@defense_router.post("/slots", response_model=DefenseSlotFull)
async def create_defense_slot(
    slot_data: DefenseSlotCreate,
    defense_service: DefenseService = Depends(get_defense_service),
    _current_user: User = Depends(require_teacher),
) -> DefenseSlotFull:
    """Создать слот по дню и номеру (только преподаватель)."""
    try:
        slot = await defense_service.create_slot(slot_data)
    except ValueError as e:
        msg = str(e)
        if "day not found" in msg or "Defense day not found" in msg or "Project type not found" in msg:
            raise HTTPException(status_code=404, detail=msg) from e
        raise HTTPException(status_code=400, detail=msg) from e
    return DefenseSlotFull.model_validate(slot)


@defense_router.get("/my-registrations", response_model=MyDefenseListResponse)
async def list_my_defenses(
    defense_service: DefenseService = Depends(get_defense_service),
    current_user: User = Depends(get_current_user),
) -> MyDefenseListResponse:
    """Получить список защит, на которые записан текущий пользователь."""
    registrations = await defense_service.get_my_registrations(user_id=current_user.id)
    items = []
    for reg in registrations:
        slot = reg.slot
        day = slot.defense_day
        items.append(
            MyDefenseItem(
                registration_id=reg.id,
                slot_id=slot.id,
                defense_day_id=slot.defense_day_id,
                slot_index=slot.slot_index,
                title=slot.title,
                project_type=ProjectTypeInfo.model_validate(slot.project_type),
                start_at=slot.start_at,
                end_at=slot.end_at,
                location=slot.location,
                defense_date=day.date,
            )
        )
    return MyDefenseListResponse(items=items)


@defense_router.post("/slots/{slot_id}/register", response_model=DefenseRegistrationFull)
async def register_for_defense(
    slot_id: int,
    _body: DefenseRegistrationCreate,
    defense_service: DefenseService = Depends(get_defense_service),
    current_user: User = Depends(get_current_user),
) -> DefenseRegistrationFull:
    """Записать текущего пользователя на защиту в указанный слот."""
    try:
        registration = await defense_service.register_user_to_slot(user_id=current_user.id, slot_id=slot_id)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg) from e
        raise HTTPException(status_code=400, detail=msg) from e

    return DefenseRegistrationFull.model_validate(registration)


@defense_router.delete("/slots/{slot_id}/register", status_code=204)
async def unregister_from_defense(
    slot_id: int,
    defense_service: DefenseService = Depends(get_defense_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Удалить запись текущего пользователя на защиту в указанном слоте."""
    try:
        await defense_service.unregister_user_from_slot(user_id=current_user.id, slot_id=slot_id)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Registration not found") from e
        raise HTTPException(status_code=400, detail=str(e)) from e

