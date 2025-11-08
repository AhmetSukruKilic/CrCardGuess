from sqlalchemy import Integer, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from database import Base, engine
from sqlalchemy import event, select, func
from sqlalchemy.dialects.mysql import DATETIME


class Player(Base):
    __tablename__ = "players"
    user_code: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=True)

    # MANY-TO-MANY with Decks via player_decks
    decks: Mapped[list["Deck"]] = relationship(
        "Deck", secondary="player_decks", back_populates="players"
    )

    # Explicit one-to-manys for each FK in Battle
    battles_as_first: Mapped[list["Battle"]] = relationship(
        "Battle",
        foreign_keys=lambda: [Battle.first_player_code],
        back_populates="first_player",
        passive_deletes=True,
    )
    battles_as_second: Mapped[list["Battle"]] = relationship(
        "Battle",
        foreign_keys=lambda: [Battle.second_player_code],
        back_populates="second_player",
        passive_deletes=True,
    )


class Card(Base):
    __tablename__ = "cards"
    card_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(255))
    decks: Mapped[list["Deck"]] = relationship(
        "Deck", secondary="deck_cards", back_populates="cards"
    )


class Battle(Base):  # 1v1 battle record
    __tablename__ = "battles"

    battle_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    # Two FKs to players → must disambiguate in relationships
    first_player_code: Mapped[str] = mapped_column(
        ForeignKey("players.user_code", ondelete="CASCADE"), index=True
    )
    second_player_code: Mapped[str] = mapped_column(
        ForeignKey("players.user_code", ondelete="CASCADE"), index=True
    )

    # Optional FKs to decks
    first_deck_id: Mapped[int | None] = mapped_column(
        ForeignKey("decks.deck_id", ondelete="SET NULL"), nullable=True
    )
    second_deck_id: Mapped[int | None] = mapped_column(
        ForeignKey("decks.deck_id", ondelete="SET NULL"), nullable=True
    )

    battle_type: Mapped[str] = mapped_column(String(50))
    battle_time: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6), nullable=False, default=datetime.now
    )

    # Disambiguated relationships back to Player
    first_player: Mapped["Player"] = relationship(
        "Player",
        foreign_keys=[first_player_code],
        back_populates="battles_as_first",
    )
    second_player: Mapped["Player"] = relationship(
        "Player",
        foreign_keys=[second_player_code],
        back_populates="battles_as_second",
    )

    # Deck relationships
    first_deck: Mapped["Deck"] = relationship("Deck", foreign_keys=[first_deck_id])
    second_deck: Mapped["Deck"] = relationship("Deck", foreign_keys=[second_deck_id])

    # Helpful composite index for queries
    __table_args__ = (Index("ix_battles_time_type", "battle_time", "battle_type"),)


class Deck(Base):
    __tablename__ = "decks"
    deck_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.now)

    # global identity of a deck (sorted 8 card IDs, e.g. "1-5-8-12-23-31-44-60")
    signature: Mapped[str] = mapped_column(String(128), unique=True, index=True)

    players: Mapped[list["Player"]] = relationship(
        "Player", secondary="player_decks", back_populates="decks"
    )
    cards: Mapped[list["Card"]] = relationship(
        "Card", secondary="deck_cards", back_populates="decks"
    )


class PlayerDeck(Base):
    __tablename__ = "player_decks"
    player_code: Mapped[str] = mapped_column(
        ForeignKey("players.user_code", ondelete="CASCADE"), primary_key=True
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("decks.deck_id", ondelete="CASCADE"), primary_key=True
    )


class DeckCard(Base):
    __tablename__ = "deck_cards"
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("decks.deck_id", ondelete="CASCADE"), primary_key=True
    )
    card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.card_id", ondelete="CASCADE"), primary_key=True
    )

    @classmethod
    def __declare_last__(cls):
        def _check_deck_size(connection, target):
            stmt = (
                select(func.count())
                .select_from(cls.__table__)
                .where(cls.__table__.c.deck_id == target.deck_id)
            )
            count = connection.execute(stmt).scalar_one()
            if count >= 8:
                raise ValueError("A deck cannot have more than 8 cards")

        event.listen(cls, "before_insert", _check_deck_size)
        event.listen(cls, "before_update", _check_deck_size)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
