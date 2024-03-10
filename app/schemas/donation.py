from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, Extra
from typing_extensions import Annotated


class DonationCreate(BaseModel):
    full_amount: Annotated[int, Field(gt=0, nullable=False)]
    comment: Optional[str] = Field('string')

    class Config:
        extra = Extra.forbid
        orm_mode = True


class DonationCreateResponse(DonationCreate):
    id: int
    create_date: datetime


class DonationDB(DonationCreateResponse):
    user_id: int
    invested_amount: int = Field(0)
    fully_invested: bool = Field(False)
    close_date: Optional[datetime]
