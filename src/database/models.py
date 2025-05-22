from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    # Добавляем обратную связь
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    # Связь к роли
    role = relationship("Role", back_populates="users")

    requests_count: Mapped[int] = mapped_column(default=0, nullable=False, server_default="0")