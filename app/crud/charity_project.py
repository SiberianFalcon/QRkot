from typing import Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase, ModelType, UpdateSchemaType
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, dict],
        db_session: AsyncSession,
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def get_projects_by_completion_rate(
        self,
        db_session
    ):
        projects = await db_session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested).order_by(
                func.julianday(CharityProject.close_date) -
                func.julianday(CharityProject.create_date)
            )
        )
        projects = projects.scalars().all()

        return projects


charityproject_crud = CRUDCharityProject(CharityProject)
