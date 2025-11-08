import requests
from app.api_funcs.api_config import HEADERS, BASE_URL, health_check


def get_cards():
    after_fix = "cards"
    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    print("Error:", resp.status_code, resp.text[:300])
    return None


def main():
    if not health_check():
        return

    cards = get_cards()
    if cards:
        for card in cards:
            print(
                f"{card.get('id')} — {card.get('name')} — Rarity: {card.get('rarity')}"
            )
    else:
        print("Card data could not be retrieved.")


if __name__ == "__main__":
    main()
