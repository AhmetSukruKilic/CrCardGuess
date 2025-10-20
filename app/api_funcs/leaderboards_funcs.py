import requests
from api_config import CR_API, BASE_URL


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


def main():
    season_id = get_season_idies().get("items")[-1].get("uniqueId")
    print("Latest Season ID:", season_id)

    top_players = get_top_players_at_season(season_id, limit=10)
    if top_players:
        for player in top_players.get("items", []):
            print(f"{player.get('tag')} — {player.get('name')}")
    else:
        print("Player data could not be retrieved.")


if __name__ == "__main__":
    main()
