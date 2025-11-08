from models import Player


def get_teammates(match: dict) -> list[dict]:
    return match.get("team", [])


def get_opponents(match: dict) -> list[dict]:
    return match.get("opponent", [])


def new_player(player_data: dict) -> Player:
    return Player(
        user_code=player_data["tag"],
        name=player_data["name"],
        rank=player_data.get("rank"),
    )
