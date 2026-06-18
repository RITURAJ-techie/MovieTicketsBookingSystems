from sqlalchemy import Column, Integer, String, Date,Enum ,Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.constants.enums import GenderEnum
from app.models.postgres import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    phone_no = Column(String, index=True, unique=True,nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    bday = Column(Date, nullable=True)
    identity = Column(Enum(GenderEnum) , nullable=True)
    is_married = Column(Boolean, nullable=True)
    pincode = Column(Integer, nullable=True)
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    landmark = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(Integer,ForeignKey("locations.location_id"))
    signed_in = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint(
            'email IS NOT NULL OR phone_no IS NOT NULL',
            name="check_email_phone_not_null"
        ),
    )

    locations = relationship("Location", back_populates="users")
    