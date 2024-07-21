import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, UUID, Boolean

from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    contact_inf = Column(String, nullable=True)
    gender = Column(String, nullable=False)
    birthdate = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    avatar_id = Column(Integer, nullable=False)
