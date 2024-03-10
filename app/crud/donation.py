from typing import Optional


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):

    async def get_by_user(
        self,
        user: User,
        db_session: AsyncSession,
    ):
        get_from_base = await db_session.execute(select(Donation).where(
            Donation.user_id == user.id
        ))
        get_donations = get_from_base.scalars().all()
        return get_donations

    async def add_create(
            self,
            obj_in,
            db_session: AsyncSession,
            user: Optional[User] = None
    ):
        db_obj = self.model(**obj_in)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


donation_crud = CRUDDonation(Donation)
