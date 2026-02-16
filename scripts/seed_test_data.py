#!/usr/bin/env python3
"""Скрипт для заполнения тестовыми данными: преподаватель, студент, проект, участие.
Запуск из корня проекта: python scripts/seed_test_data.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal, engine
from src.model.models import Project, ProjectParticipation, User


# Пароль для обоих тестовых пользователей (для входа в Swagger)
TEST_PASSWORD = "test1234"


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        pwd = PasswordHash.recommended()
        password_hashed = pwd.hash(TEST_PASSWORD)

        # Преподаватель (evaluator)
        teacher = User(
            first_name="Преподаватель",
            middle_name="Тест",
            last_name="Иванов",
            email="teacher@test.com",
            password_hashed=password_hashed,
        )
        session.add(teacher)
        await session.flush()

        # Студент (participant)
        student = User(
            first_name="Студент",
            middle_name="Тест",
            last_name="Петров",
            email="student@test.com",
            password_hashed=password_hashed,
        )
        session.add(student)
        await session.flush()

        # Проект (владелец — студент)
        project = Project(
            name="Тестовый проект для оценивания",
            author_id=student.id,
            description="Проект создан скриптом seed_test_data.py",
        )
        session.add(project)
        await session.flush()

        # Участие студента в проекте
        participation = ProjectParticipation(
            project_id=project.id,
            participant_id=student.id,
        )
        session.add(participation)

        await session.commit()

        print("ID проекта:", project.id)
        print("ID студента:", student.id)
        print("ID преподавателя:", teacher.id)
        print()
        print("Логин в Swagger: teacher@test.com или student@test.com, пароль:", TEST_PASSWORD)


async def main() -> None:
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
