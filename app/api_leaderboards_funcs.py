import requests

from api_config import HEADERS, BASE_URL, health_check
from service_battle_funcs import get_first_enemy_cards, get_first_teammate_cards
from api_player_funcs import (
    get_player_battlelog,
)


def get_season_idies():
    after_fix = "locations/global/seasonsV2"
    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    print("Error:", resp.status_code, resp.text[:300])
    return None


def get_latest_season_id():
    seasons = get_season_idies()
    if seasons:
        return seasons[-1]["uniqueId"]
    return None


def get_top_players_at_season(season_id=get_latest_season_id(), limit=100):
    after_fix = (
        f"locations/global/pathoflegend/{season_id}/rankings/players?limit={limit}"
    )
    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    print("Error:", resp.status_code, resp.text[:300])
    return None


def main():
    if not health_check():
        return

    season_id = get_latest_season_id()
    print("Latest Season ID:", season_id)

    top_players = get_top_players_at_season(season_id, limit=10)
    if top_players:
        for player in top_players:
            tag = player.get("tag")
            name = player.get("name")
            print(f"{tag} — {name}")

            battle_log = get_player_battlelog(tag)
            for battle in battle_log[:3]:
                print(f"Your cards:")
                for card in get_first_teammate_cards(battle):
                    print(f" {card.name} ", end="")
                print(f"\n\nEnemy cards:")
                for card in get_first_enemy_cards(battle):
                    print(f" {card.name} ", end="")
                print("\n\n")
    else:
        print("Player data could not be retrieved.")


if __name__ == "__main__":
    main()
