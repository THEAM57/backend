from __future__ import annotations

from sqlalchemy import func, select

from src.core.uow import IUnitOfWork
from src.model.models import GradingCriteria
from src.repository.base_repository import BaseRepository


class GradingCriteriaRepository(BaseRepository[GradingCriteria, dict, dict]):
    """Репозиторий для работы с критериями оценивания"""

    def __init__(self, uow: IUnitOfWork):
        """Инициализация репозитория

        Args:
            uow: Unit of Work для управления транзакциями
        """
        super().__init__(uow)
        self._model = GradingCriteria

    async def get_by_project_type(self, project_type_id: int) -> list[GradingCriteria]:
        """Получить все критерии для типа проекта

        Args:
            project_type_id: ID типа проекта

        Returns:
            Список критериев оценивания, отсортированный по order_index
        """
        result = await self.uow.session.execute(
            select(GradingCriteria)
            .where(GradingCriteria.project_type_id == project_type_id)
            .order_by(GradingCriteria.order_index)
        )
        criteria = list(result.scalars().all())
        return criteria

    async def get_total_max_score(self, project_type_id: int) -> int:
        """Получить суммарный максимальный балл с учётом весов

        Args:
            project_type_id: ID типа проекта

        Returns:
            Сумма (max_score * weight) для всех критериев
        """
        result = await self.uow.session.execute(
            select(func.sum(GradingCriteria.max_score * GradingCriteria.weight)).where(
                GradingCriteria.project_type_id == project_type_id
            )
        )
        total = result.scalar()
        return total if total else 0

    async def exists_by_name(
        self, project_type_id: int, name: str, exclude_id: int | None = None
    ) -> bool:
        """Проверить существование критерия с таким именем

        Args:
            project_type_id: ID типа проекта
            name: Название критерия
            exclude_id: ID критерия для исключения из проверки (для update)

        Returns:
            True если критерий с таким именем уже существует
        """
        result = await self.uow.session.execute(
            select(GradingCriteria).where(
                GradingCriteria.project_type_id == project_type_id, GradingCriteria.name == name
            )
        )
        existing = result.scalar_one_or_none()

        if not existing:
            return False

        if exclude_id and existing.id == exclude_id:
            return False

        return True
