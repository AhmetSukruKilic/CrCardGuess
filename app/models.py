from sqlalchemy import Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from database import Base


class Player(Base):
    __tablename__ = "players"

    user_code: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=True)
    # Relationships
    decks: Mapped[list["Deck"]] = relationship("Deck", back_populates="player")
    battles: Mapped[list["Battle"]] = relationship("Battle", back_populates="player")


class Card(Base):
    __tablename__ = "cards"

    card_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(255))

    # Optional backref to decks if you add a many-to-many later
    decks = relationship("Deck", secondary="deck_cards", back_populates="cards")


class Battle(Base):
    __tablename__ = "battles"

    battle_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    player_code: Mapped[str] = mapped_column(
        ForeignKey("players.user_code", ondelete="CASCADE")
    )
    battle_type: Mapped[str] = mapped_column(String(50))
    battle_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    raw_data: Mapped[dict] = mapped_column(JSON)  # store raw API payload (optional)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="battles")


class Deck(Base):
    __tablename__ = "decks"

    deck_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    player_code: Mapped[str] = mapped_column(
        ForeignKey("players.user_code", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="decks")
    cards: Mapped[list[Card]] = relationship(
        "Card", secondary="deck_cards", back_populates="decks"
    )
