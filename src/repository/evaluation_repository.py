from __future__ import annotations

from sqlalchemy import select

from src.core.uow import IUnitOfWork
from src.model.models import Evaluation
from src.repository.base_repository import BaseRepository
from src.schema.evaluation import EvaluationCreate, EvaluationUpdate


class EvaluationRepository(BaseRepository[Evaluation, EvaluationCreate, EvaluationUpdate]):
    """Репозиторий для работы с оценками проектов."""

    def __init__(self, uow: IUnitOfWork) -> None:
        super().__init__(uow)
        self._model = Evaluation

    async def get_by_project_id(self, project_id: int) -> list[Evaluation]:
        """Получить все оценки по проекту."""

        result = await self.uow.session.execute(select(Evaluation).where(Evaluation.project_id == project_id))
        return list(result.scalars().all())

    async def get_by_project_and_participant(self, project_id: int, participant_id: int) -> list[Evaluation]:
        """Получить оценки конкретного участника по проекту."""

        result = await self.uow.session.execute(
            select(Evaluation).where(
                Evaluation.project_id == project_id,
                Evaluation.participant_id == participant_id,
            )
        )
        return list(result.scalars().all())

