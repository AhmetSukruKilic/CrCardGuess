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


def main():
    player = get_player("#Q8PRJJ92")
    battle_log = get_player_battlelog("#Q8PRJJ92")
    if player:
        print(f"{player.get('tag')} — {player.get('name')}")
    else:
        print("Player data could not be retrieved.")

    if battle_log and player:
        for battle in battle_log[:5]:
            team_cards = []
            for member in battle.get("team", []):
                if member.get("tag") == player.get("tag"):
                    team_cards = [c.get("name") for c in member.get("cards", [])]
                    break

            opponent_cards = []
            opponents = battle.get("opponent") or []
            if opponents:
                opp = opponents[0]
                opponent_cards = [c.get("name") for c in opp.get("cards", [])]

            print(f"Your Cards: {team_cards} vs \nEnemy Cards: {opponent_cards}\n\n\n")

    print(len(battle_log))


if __name__ == "__main__":
    main()
