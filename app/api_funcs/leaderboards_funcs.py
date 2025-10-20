import requests
from api_config import CR_API, BASE_URL
from player_funcs import (
    get_player_battlelog,
    get_team_cards_from_battles,
    get_opponent_cards_from_battles,
)


def get_top_players_at_season(season_id, limit=100):
    after_fix = (
        f"locations/global/pathoflegend/{season_id}/rankings/players?limit={limit}"
    )
    url = f"{BASE_URL}/{after_fix}"

    headers = {
        "Authorization": f"Bearer {CR_API}",
    }
    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code == 200:
        return resp.json()
    print("Error:", resp.status_code, resp.text[:300])
    return None


def get_season_idies():
    after_fix = "locations/global/seasonsV2"
    url = f"{BASE_URL}/{after_fix}"

    headers = {
        "Authorization": f"Bearer {CR_API}",
    }
    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code == 200:
        return resp.json()
    print("Error:", resp.status_code, resp.text[:300])
    return None


def get_latest_season_id():
    seasons = get_season_idies()
    if seasons and "items" in seasons:
        return seasons["items"][-1]["uniqueId"]
    return None


def main():
    season_id = get_latest_season_id()
    print("Latest Season ID:", season_id)

    top_players = get_top_players_at_season(season_id, limit=10)
    if top_players:
        for player in top_players.get("items", []):
            tag = player.get("tag")
            name = player.get("name")
            print(f"{tag} — {name}")

            battle_log = get_player_battlelog(tag)
            for battle in battle_log[:3]:
                team_cards = get_team_cards_from_battles(battle)
                opponent_cards = get_opponent_cards_from_battles(battle)
                print(
                    f"Your Cards: {team_cards} vs \nEnemy Cards: {opponent_cards}\n\n\n"
                )
    else:
        print("Player data could not be retrieved.")


if __name__ == "__main__":
    main()
