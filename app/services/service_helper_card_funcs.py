from app.db.models import Card


def create_sorted_cards(db, cards: list[str]) -> list[Card]:
    card_list = []
    for card_name in cards:
        card = get_card_by_name(db, card_name)
        if card:
            card_list.append(card)
    card_list.sort(key=lambda x: x.card_id)
    return card_list


# module-level caches
cache_by_id: dict[int, Card] = {}
cache_by_name: dict[str, Card] = {}


def _remember(card: "Card") -> "Card":
    if card is None:
        return None
    cache_by_id[card.card_id] = card
    cache_by_name[card.name] = card
    return card


def get_card_by_name(db, card_name: str) -> "Card | None":
    if not isinstance(card_name, str):
        # Defensive: accept Card or anything else but convert to name
        if hasattr(card_name, "name"):
            card_name = card_name.name
        else:
            raise TypeError(f"card_name must be str or Card, got {type(card_name)}")

    cached = cache_by_name.get(card_name)
    if cached:
        return cached

    card = db.query(Card).filter(Card.name == card_name).first()
    return _remember(card) if card else None


def get_card_by_id(db, card_id: int) -> "Card | None":
    if not isinstance(card_id, int):
        # Defensive: accept Card or anything else but convert to id
        if hasattr(card_id, "card_id"):
            card_id = card_id.card_id
        else:
            raise TypeError(f"card_id must be int or Card, got {type(card_id)}")

    cached = cache_by_id.get(card_id)
    if cached:
        return cached

    card = db.query(Card).filter(Card.card_id == card_id).first()
    return _remember(card) if card else None
