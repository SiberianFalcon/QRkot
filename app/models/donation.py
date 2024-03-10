from sqlalchemy import Column, Integer, ForeignKey, Text

from app.core.db import Base, GeneralClassForProjectAndDonation


class Donation(Base, GeneralClassForProjectAndDonation):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text, default='string')
