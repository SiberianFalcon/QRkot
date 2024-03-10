from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_closed_project, check_project_not_empty,
    check_that_full_amount_not_less_invested, check_unique_name,
    object_not_found
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charityproject_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.service.calculate import calculate_create_project

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def create_project(
    request: Request,
    charity_project: CharityProjectCreate,
    db_session: AsyncSession = Depends(get_async_session)
):
    await check_unique_name(charity_project, db_session=db_session)
    new_project = await charityproject_crud.create(
        charity_project, db_session
    )
    calculate_result = await calculate_create_project(
        new_project,
        db_session
    )
    update_data = await charityproject_crud.update(
        new_project,
        calculate_result,
        db_session
    )
    return update_data


@router.get(
    '/',
    response_model=list[CharityProjectDB]
)
async def get_all_projects(
    db_session: AsyncSession = Depends(get_async_session)
):
    get_all = await charityproject_crud.get_multi(db_session)
    return get_all


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_project(
    request: Request,
    project_id: int,
    db_session: AsyncSession = Depends(get_async_session)
):
    get_project = await charityproject_crud.get(project_id, db_session)
    if get_project is None:
        await object_not_found()
    if get_project.fully_invested:
        await check_closed_project(get_project, request)
    await check_project_not_empty(get_project)
    get_project = await charityproject_crud.remove(
        get_project, db_session
    )

    return get_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def update_project(
    request: Request,
    project_id: int,
    project_obj: CharityProjectUpdate,
    db_session: AsyncSession = Depends(get_async_session)
):
    get_project = await charityproject_crud.get(project_id, db_session)
    if get_project is None:
        await object_not_found()
    await check_closed_project(get_project, request)
    if project_obj.name:
        await check_unique_name(project_obj, db_session)
    if project_obj.full_amount:
        await check_that_full_amount_not_less_invested(
            get_project,
            project_obj
        )

    updated_project = await charityproject_crud.update(
        db_obj=get_project,
        obj_in=project_obj,
        db_session=db_session
    )
    return updated_project
