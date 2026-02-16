from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from src.core.exceptions import NotFoundError
from src.model.models import Evaluation
from src.repository.project_repository import ProjectRepository
from src.schema.evaluation import (
    EvaluationCreate,
    EvaluationFull,
    EvaluationResultItem,
    EvaluationResultsResponse,
    EvaluationUpdate,
)
from src.services.base_service import BaseService

if TYPE_CHECKING:
    from src.repository.evaluation_repository import EvaluationRepository


class EvaluationService(BaseService[Evaluation, EvaluationCreate, EvaluationUpdate]):
    """Сервис для работы с оценками и результатами."""

    def __init__(
        self,
        evaluation_repository: EvaluationRepository,
        project_repository: ProjectRepository,
    ):
        super().__init__(evaluation_repository)
        self._evaluation_repository = evaluation_repository
        self._project_repository = project_repository

    async def create_evaluation(self, evaluation_data: EvaluationCreate, evaluator_id: int) -> Evaluation:
        """Создать новую оценку (форма оценивания).

        evaluator_id берётся из текущего пользователя.
        """
        project = await self._project_repository.get_by_id(evaluation_data.project_id)
        if not project:
            raise NotFoundError(f"Project with id {evaluation_data.project_id} not found")

        # Считаем суммарный балл по всем критериям
        total_score = int(sum(evaluation_data.scores.values()))

        data = evaluation_data.model_dump()
        data["evaluator_id"] = evaluator_id
        data["total_score"] = total_score

        return await self._evaluation_repository.create(data)

    async def get_evaluation_by_id(self, evaluation_id: int) -> Evaluation | None:
        """Получить оценку по ID."""

        return await self._evaluation_repository.get_by_id(evaluation_id)

    async def get_results_for_project(self, project_id: int) -> EvaluationResultsResponse:
        """Получить сводные результаты по проекту (форма представления результатов)."""

        evaluations = await self._evaluation_repository.get_by_project_id(project_id)

        grouped: dict[int, list[Evaluation]] = defaultdict(list)
        for evaluation in evaluations:
            grouped[evaluation.participant_id].append(evaluation)

        items: list[EvaluationResultItem] = []
        for participant_id, participant_evaluations in grouped.items():
            if not participant_evaluations:
                continue

            total_sum = sum(e.total_score for e in participant_evaluations)
            count = len(participant_evaluations)
            average_score = float(total_sum) / count if count > 0 else 0.0

            items.append(
                EvaluationResultItem(
                    project_id=project_id,
                    participant_id=participant_id,
                    average_score=average_score,
                    evaluations_count=count,
                )
            )

        return EvaluationResultsResponse(items=items)

