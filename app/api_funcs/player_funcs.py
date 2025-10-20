import os
import sys
import requests
from api_config import HEADERS, BASE_URL
import requests

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from helper_battle_funcs import (
    get_team_cards_from_battles,
    get_opponent_cards_from_battles,
)


def get_player(player_tag):
    if player_tag is None:
        raise ValueError("player_tag must be provided")

    if player_tag.startswith("#"):
        player_tag = player_tag.replace("#", "%23")

    after_fix = f"players/{player_tag}"

    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.json()

    print("Error:", resp.status_code, resp.text[:300])
    return None


def get_player_battlelog(player_tag):
    if player_tag is None:
        raise ValueError("player_tag must be provided")

    if player_tag.startswith("#"):
        player_tag = player_tag.replace("#", "%23")

    after_fix = f"players/{player_tag}/battlelog"

    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.json()

    print("Error:", resp.status_code, resp.text[:300])
    return None


def main():
    player = get_player("#Q8PRJJ92")
    battle_log = get_player_battlelog("#Q8PRJJ92")
    if player:
        print(f"{player.get('tag')} — {player.get('name')}")
    else:
        print("Player data could not be retrieved.")

    if battle_log and player:
        for battle in battle_log[:5]:
            team_cards = get_team_cards_from_battles(battle)

            opponent_cards = get_opponent_cards_from_battles(battle)

            print(f"Your Cards: {team_cards} vs \nEnemy Cards: {opponent_cards}\n\n\n")

    print(len(battle_log))


if __name__ == "__main__":
    main()
