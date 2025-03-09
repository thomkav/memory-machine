"""
This module defines database models for the memory-machine application.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import SchemaSpecificBaseModel


class Library(SchemaSpecificBaseModel):
    """Library model representing a collection of resources."""

    __tablename__ = "libraries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="library")


class User(SchemaSpecificBaseModel):
    """User model representing application users."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    library_id: Mapped[Optional[int]] = mapped_column(ForeignKey("libraries.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    library: Mapped["Library"] = relationship(back_populates="users")
    researcher_profile: Mapped[Optional["Researcher"]] = relationship(
        uselist=False, back_populates="user"
    )


class Researcher(SchemaSpecificBaseModel):
    """Researcher model extending user information for research purposes."""

    __tablename__ = "researchers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(100))
    years_of_experience: Mapped[Optional[int]] = mapped_column()
    specialization: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="researcher_profile")
