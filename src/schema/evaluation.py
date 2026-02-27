from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationBase(BaseModel):
    """Базовая схема оценки проекта."""

    project_id: int
    participant_id: int
    scores: dict[str, int] = Field(
        default_factory=dict,
        description='Оценки по критериям в формате {"criterion_key": score}',
    )
    comment: str | None = None


class EvaluationCreate(EvaluationBase):
    """Схема для создания оценки (форма оценивания)."""

    # evaluator_id берём из текущего пользователя, поэтому в форме не передаём
    pass


class EvaluationUpdate(BaseModel):
    """Схема для обновления оценки."""

    scores: dict[str, int] | None = None
    comment: str | None = None


class EvaluationFull(EvaluationBase):
    """Полная схема оценки."""

    id: int
    evaluator_id: int
    total_score: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationResultItem(BaseModel):
    """Элемент результата для участника по проекту."""

    project_id: int
    participant_id: int
    average_score: float
    evaluations_count: int


class EvaluationResultsResponse(BaseModel):
    """Сводные результаты оценивания по проекту (форма представления результатов)."""

    items: list[EvaluationResultItem]
