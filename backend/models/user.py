from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)  # NULL for legacy/demo users
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    activity_level = Column(String(50), nullable=True)
    goals = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    assessments = relationship("HealthAssessment", back_populates="user")
    chats = relationship("ChatHistory", back_populates="user")
    workout_plans = relationship("WorkoutPlan", back_populates="user")
    meals = relationship("MealLog", back_populates="user")

