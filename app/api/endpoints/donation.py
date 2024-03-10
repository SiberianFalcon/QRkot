from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import (
    DonationDB, DonationCreate, DonationCreateResponse
)
from app.service.calculate import calculate_create_donation

router = APIRouter()


@router.post(
    '/',
    response_model=DonationCreateResponse,
    response_model_exclude_defaults=True
)
async def create_donation(
    donation_obj: DonationCreate,
    user: User = Depends(current_user),
    db_session: AsyncSession = Depends(get_async_session)
):
    create_donat = await donation_crud.create(
        donation_obj,
        db_session,
        user
    )
    calculate_result = await calculate_create_donation(
        create_donat,
        db_session
    )
    new_obj = await donation_crud.update(
        create_donat,
        calculate_result,
        db_session
    )
    return new_obj


@router.get(
    '/',
    response_model=list[DonationDB],
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    db_session: AsyncSession = Depends(get_async_session)
):
    get_all = await donation_crud.get_multi(db_session)
    return get_all


@router.get(
    '/my',
    response_model=list[DonationCreateResponse],
    response_model_exclude={'user_id'}
)
async def get_users_donations(
    user_id: User = Depends(current_user),
    db_session: AsyncSession = Depends(get_async_session),
):
    get_user = await donation_crud.get_by_user(user_id, db_session=db_session)
    return get_user
