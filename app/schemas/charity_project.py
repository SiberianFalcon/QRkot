from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, Extra


class CharityProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, nullable=False)


class CharityProjectCreate(CharityProjectBase):
    description: str = Field(
        ...,
        min_length=1,
        nullable=False
    )
    full_amount: int = Field(..., gt=0, nullable=False)

    class Config:
        extra = Extra.forbid
        orm_mode = True


class CharityProjectUpdate(CharityProjectCreate):
    name: Optional[str] = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        min_length=1,
        nullable=False
    )
    full_amount: Optional[int] = Field(gt=0, nullable=False)


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]
