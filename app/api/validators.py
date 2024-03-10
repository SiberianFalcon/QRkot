from typing import Union

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import ModelType
from app.models import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate
)


async def check_closed_project(
    obj_in: CharityProject,
    request: Request
):
    if obj_in.fully_invested is True:
        if request.method == 'PATCH':
            type_of_response = 'редактировать'
        else:
            type_of_response = 'удалить'
        raise HTTPException(
            status_code=400,
            detail=f'Невозможно {type_of_response} завершённый проект.'
        )


async def check_project_not_empty(
    project: ModelType
):
    if project.invested_amount != 0:
        raise HTTPException(
            status_code=400,
            detail='Невозможно удалить проект с внесёнными деньгами.'
        )


async def check_that_full_amount_not_less_invested(
    project: CharityProject,
    new_data: CharityProjectUpdate
):
    if new_data.full_amount is None:
        return

    if project.invested_amount > new_data.full_amount:
        raise HTTPException(
            status_code=422,
            detail=(
                'Запрещено устанавливать требуемую сумму меньше внесённой.')
        )


async def check_unique_name(
    obj_in: Union[CharityProjectCreate, CharityProjectUpdate],
    db_session: AsyncSession,
):

    if obj_in.name is not None:
        get_obj = await db_session.execute(select(CharityProject).where(
            CharityProject.name == obj_in.name))
        get_obj = get_obj.scalars().first()
        if get_obj is not None:
            raise HTTPException(
                status_code=400,
                detail='Имя проекта уже существует.'
            )


async def object_not_found(
):
    raise HTTPException(
        status_code=404,
        detail='Объект не найден.'
    )
