from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.container import get_evaluation_service
from src.core.dependencies import get_current_user, setup_audit
from src.core.exceptions import NotFoundError
from src.model.models import User
from src.schema.evaluation import EvaluationCreate, EvaluationFull, EvaluationResultsResponse
from src.services.evaluation_service import EvaluationService

evaluation_router = APIRouter(prefix="/evaluations", tags=["evaluation"])


@evaluation_router.post("/", response_model=EvaluationFull, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
    current_user: User = Depends(get_current_user),
    _audit=Depends(setup_audit),
) -> EvaluationFull:
    """Создать новую оценку для участника проекта (форма оценивания)."""

    try:
        evaluation = await evaluation_service.create_evaluation(evaluation_data, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail)) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create evaluation: {e!s}",
        ) from e

    return EvaluationFull.model_validate(evaluation)


@evaluation_router.get("/results/by-project/{project_id}", response_model=EvaluationResultsResponse)
async def get_project_results(
    project_id: int,
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
    _current_user: User = Depends(get_current_user),
) -> EvaluationResultsResponse:
    """Получить сводные результаты оценивания по проекту (форма представления результатов)."""

    results = await evaluation_service.get_results_for_project(project_id)
    return results

