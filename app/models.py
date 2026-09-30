from sqlalchemy import Column, Integer, String, Text
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(String(20), nullable=False)
    goal = Column(String(50), nullable=False)
    intensity = Column(String(20), nullable=False)

    original_plan = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)