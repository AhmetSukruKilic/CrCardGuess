from app.db.models import Card

cached_cards = {}


def create_sorted_cards(db, cards: list[str]) -> list[Card]:
    card_list = []
    for card_name in cards:
        card = get_card_by_name(db, card_name)
        if card:
            card_list.append(card)
    card_list.sort(key=lambda x: x.card_id)
    return card_list


def get_card_by_name(db, card_name: str) -> Card | None:
    for card in cached_cards.values():
        if card.name == card_name:
            return card
    card = db.query(Card).filter(Card.name == card_name).first()
    if card:
        cached_cards[card] = card
    return card


def get_card_by_id(db, card_id: int) -> Card | None:
    for card in cached_cards.values():
        if card.card_id == card_id:
            print(1)
            return card
    card = db.query(Card).filter(Card.card_id == card_id).first()
    if card:
        cached_cards[card] = card
    return card
