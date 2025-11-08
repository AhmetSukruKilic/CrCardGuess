from app.db.models import Card
from app.services.service_helper_card_funcs import create_sorted_cards
from app.db.models import Player
from app.services.service_helper_player_funcs import get_teammates, get_opponents

BATTLE_TYPE = "type"
BATTLE_TIME = "battleTime"


def get_team_cards_from_battles(db, battle) -> list[list[Card]]:
    members = get_teammates(battle)
    player_cards = []

    for member in members:
        member_cards = [c.get("name") for c in member.get("cards", [])]
        player_cards.append(create_sorted_cards(db, member_cards))
    return player_cards


def get_opponent_cards_from_battles(db, battle) -> list[list[Card]]:
    members = get_opponents(battle)
    opponent_cards = []

    for member in members:
        member_cards = [c.get("name") for c in member.get("cards", [])]
        opponent_cards.append(create_sorted_cards(db, member_cards))
    return opponent_cards


def get_first_teammate_cards(db, battle) -> list[Card]:
    all_cards = get_team_cards_from_battles(db, battle)
    return all_cards[0] if all_cards else []


def get_first_enemy_cards(db, battle) -> list[Card]:
    all_cards = get_opponent_cards_from_battles(db, battle)
    return all_cards[0] if all_cards else []


def get_second_teammate_cards(db, battle) -> list[Card]:
    all_cards = get_team_cards_from_battles(db, battle)
    return all_cards[1] if len(all_cards) > 1 else []


def get_second_enemy_cards(db, battle) -> list[Card]:
    all_cards = get_opponent_cards_from_battles(db, battle)
    return all_cards[1] if len(all_cards) > 1 else []


def get_first_teammate_data(match: dict) -> dict | None:
    teammates = get_teammates(match)
    return teammates[0] if teammates else None


def get_first_opponent_data(match: dict) -> dict | None:
    opponents = get_opponents(match)
    return opponents[0] if opponents else None


def get_second_teammate_data(match: dict) -> dict | None:
    teammates = get_teammates(match)
    return teammates[1] if len(teammates) > 1 else None


def get_second_opponent_data(match: dict) -> dict | None:
    opponents = get_opponents(match)
    return opponents[1] if len(opponents) > 1 else None


def get_first_teammate_player(db, match: dict) -> Player | None:
    teammates = get_first_teammate_data(match)
    teammate_player = (
        db.query(Player).filter(Player.user_code == teammates.get("tag")).first()
    )
    return teammate_player if teammate_player else None


def get_first_opponent_player(db, match: dict) -> Player | None:
    opponents = get_first_opponent_data(match)
    opponent_player = (
        db.query(Player).filter(Player.user_code == opponents.get("tag")).first()
    )
    return opponent_player if opponent_player else None


def get_second_teammate_player(db, match: dict) -> Player | None:
    teammates = get_second_teammate_data(match)
    teammate_player = (
        db.query(Player).filter(Player.user_code == teammates.get("tag")).first()
    )
    return teammate_player if teammate_player else None


def get_second_opponent_player(db, match: dict) -> Player | None:
    opponents = get_second_opponent_data(match)
    opponent_player = (
        db.query(Player).filter(Player.user_code == opponents.get("tag")).first()
    )
    return opponent_player if opponent_player else None
