from sqlalchemy import Column, String, Text

from app.core.db import Base, GeneralClassForProjectAndDonation


class CharityProject(Base, GeneralClassForProjectAndDonation):
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
