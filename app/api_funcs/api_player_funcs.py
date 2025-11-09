import requests

from app.api_funcs.api_config import HEADERS, BASE_URL, health_check

from app.db.database import SessionLocal
from app.services.service_battle_funcs import (
    get_first_teammate_cards,
    get_first_enemy_cards,
)


def adjust_player_tag(player_tag):
    if player_tag.startswith("#"):
        player_tag = player_tag.replace("#", "%23")
    if not player_tag.startswith("%"):
        player_tag = f"%{player_tag}"
    return player_tag


def get_player(player_tag):
    if player_tag is None:
        raise ValueError("player_tag must be provided")

    player_tag = adjust_player_tag(player_tag)

    after_fix = f"players/{player_tag}"

    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.json()

    print("Error:", resp.status_code, resp.text[:300])
    return None


def get_player_battlelog(player_tag) -> dict:
    if player_tag is None:
        raise ValueError("player_tag must be provided")

    player_tag = adjust_player_tag(player_tag)

    after_fix = f"players/{player_tag}/battlelog"

    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.json()

    print("Error:", resp.status_code, resp.text[:300])
    return None


def main():
    if not health_check():
        return

    player = get_player("#Q8PRJJ92")
    if player:
        print(f"{player.get('tag')} — {player.get('name')}")
    else:
        print("Player data could not be retrieved.")
    tag = player.get("tag")
    db = SessionLocal()
    battle_log = get_player_battlelog(tag)
    for battle in battle_log[:3]:
        print(f"Your cards:")
        for card in get_first_teammate_cards(db, battle):
            print(f" {card.name} ", end="")
        print(f"\n\nEnemy cards:")
        for card in get_first_enemy_cards(db, battle):
            print(f" {card.name} ", end="")
        print("\n\n")


if __name__ == "__main__":
    main()
