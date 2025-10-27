
from app.database import SessionLocal

from app.models import Deck,

def get_player_decks(player):
    db = SessionLocal()
    
    return (
        db.query(Deck)
        .filter(
            Deck.player_code == player.user_code,
        )
        .all()
    )