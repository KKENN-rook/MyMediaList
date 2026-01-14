from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, select, ForeignKey
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    pw_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Hash could use many chars
    media_items: Mapped[list["MediaItem"]] = relationship(back_populates="user")  # 1:M -- User:Media Items

    def set_password(self, password: str):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class MediaItem(db.Model):
    __tablename__ = "media_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Generic progress tracking
    total_units: Mapped[int | None] = mapped_column(nullable=True)
    completed_units: Mapped[int | None] = mapped_column(nullable=True)
    unit_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="media_items")


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
