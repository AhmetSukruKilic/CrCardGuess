from app.api_funcs.api_card_funcs import get_cards
from app.api_funcs.api_config import health_check
from app.db_methods.models import Card
from app.db_methods.database import SessionLocal
from sqlalchemy.exc import IntegrityError


def match_similar_cards():
    db = SessionLocal()
    pass


def register_new_cards(cards=None):
    db = SessionLocal()
    try:
        if cards is None:
            cards = get_cards()

        for card in cards:
            cid = card.get("id")
            name = card.get("name")
            url = (card.get("iconUrls") or {}).get("medium", "")

            exists = db.query(Card).get(cid)  # primary key lookup if card_id is PK
            if exists:
                continue

            db.add(Card(card_id=cid, name=name, photo_url=url))
            print(f"Added new card: {name}")

        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError → rolled back: {e}")
        # optional: continue or re-raise
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    if not health_check():
        return

    register_new_cards()


if __name__ == "__main__":
    main()
