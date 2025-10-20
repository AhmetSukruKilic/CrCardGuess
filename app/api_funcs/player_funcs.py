from collections import defaultdict
import requests
from api_config import CR_API, BASE_URL
import requests


def get_player(player_tag):
    if player_tag is None:
        raise ValueError("player_tag must be provided")

    if player_tag.startswith("#"):
        player_tag = player_tag.replace("#", "%23")

    after_fix = f"players/{player_tag}"

    url = f"{BASE_URL}/{after_fix}"

    headers = {
        "Authorization": f"Bearer {CR_API}",
    }

    resp = requests.get(url, headers=headers, timeout=20)
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

    headers = {
        "Authorization": f"Bearer {CR_API}",
    }

    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code == 200:
        return resp.json()

    print("Error:", resp.status_code, resp.text[:300])
    return None


def get_team_cards_from_battles(battle):
    members = battle.get("team") or []

    team_cards = {
        member.get("tag"): [] for member in members
    }  # assuming max 2 team members

    for i in range(0, len(members)):
        team_cards[members[i].get("tag")] = [
            c.get("name") for c in members[i].get("cards", [])
        ]
    return team_cards


def get_opponent_cards_from_battles(battle):
    opponents = battle.get("opponent") or []

    opponent_cards = {
        opponent.get("tag"): [] for opponent in opponents
    }  # assuming max 2 opponents

    for i in range(0, len(opponents)):
        opponent_cards[opponents[i].get("tag")] = [
            c.get("name") for c in opponents[i].get("cards", [])
        ]
    return opponent_cards


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
