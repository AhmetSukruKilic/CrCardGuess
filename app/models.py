from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class Players(Base):
    __tablename__ = "players"

    user_code: Mapped[str] = mapped_column(
        String, unique=True, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(String)


class Cards(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    rarity: Mapped[str] = mapped_column(String)
    photo_url: Mapped[str] = mapped_column(String)
