from database import SessionLocal
from models import Card


def create_deck(cards: list[str]):
    card_list = []
    for card_name in cards:
        card = get_card_by_name(card_name)
        if card:
            card_list.append(card)
    card_list.sort(key=lambda x: x.card_id)
    return card_list


def get_card_by_name(card_name: str):
    db = SessionLocal()
    card = db.query(Card).filter(Card.name == card_name).first()
    db.close()
    return card
