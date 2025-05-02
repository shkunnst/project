import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Create base class for declarative models
Base = declarative_base()


# Define role enum
class UserRole(str, enum.Enum):
    LEADER = "руководитель"
    SUBORDINATE = "подчиненный"
    ADMIN = "администратор"


# Department model
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relationship with users
    users = relationship("User", back_populates="department")


# WorkData model
class WorkData(Base):
    __tablename__ = "work_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    working_hours = Column(Float, default=0.0)
    bonuses = Column(Float, default=0.0)
    fines = Column(Float, default=0.0)

    # Relationship with user
    user = relationship("User", back_populates="work_data")


# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    recovery_word = Column(String)
    recovery_hint = Column(String)
    role = Column(Enum(UserRole))

    # Foreign key to department
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="users")

    # Relationship with work data
    work_data = relationship("WorkData", back_populates="user", uselist=False)
