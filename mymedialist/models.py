from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    pw_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # 255 cause Hash could use many chars
    # 1:M -- User : UserMedia (list entries) SQLAlch Can establish the relationship based on the mapping
    list_entries: Mapped[list["UserMedia"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class MediaWork(db.Model):
    """
    Global catalog item (Created manually by a user or API-backed)

    """

    __tablename__ = "media_works"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Generic "total size" of the work for progress tracking
    # books -> pages; shows -> episodes; games -> NULL
    total_units: Mapped[int | None] = mapped_column(nullable=True)
    unit_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    list_entries: Mapped[list["UserMedia"]] = relationship(back_populates="media", cascade="all, delete-orphan")

    # Prevents duplicates for API-sourced items; must have source/external_id pair must be unique.
    # Does not affect manual entries as Null values do not participate in uniqueness
    # Unique constraint must be a tuple or dict
    __table_args__ = UniqueConstraint("source", "external_id", name="uq_media_source_external_id")


class UserMedia(db.Model):
    __tablename__ = "user_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    media_id: Mapped[int] = mapped_column(ForeignKey("media_works.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress_value: Mapped[int | None] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="list_entries")
    media: Mapped["MediaWork"] = relationship(back_populates="list_entries")

    __table_args__ = UniqueConstraint("user_id", "media_id", name="uq_user_media_user_id_media_id")


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
