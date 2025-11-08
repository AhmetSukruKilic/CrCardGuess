from app.db_methods.models import Card


def create_deck(db, cards: list[str]) -> list[Card]:
    card_list = []
    for card_name in cards:
        card = get_card_by_name(db, card_name)
        if card:
            card_list.append(card)
    card_list.sort(key=lambda x: x.card_id)
    return card_list


def get_card_by_name(db, card_name: str) -> Card | None:
    card = db.query(Card).filter(Card.name == card_name).first()
    return card


def get_cards_by_ids(db, card_ids: list[int]) -> list[Card]:
    cards = db.query(Card).filter(Card.card_id.in_(card_ids)).all()
    return cards
