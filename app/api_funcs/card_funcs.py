import socket
import requests
import urllib3.util.connection as urllib3_connection
from app.api_funcs.api_settings import CR_API, BASE_URL

def _force_ipv4():
    def _family():
        return socket.AF_INET
    urllib3_connection.allowed_gai_family = _family

_force_ipv4()

def get_cards():
	after_fix = 'cards'
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
	cards = get_cards()
	if cards:
		for card in cards.get("items", []):
			print(f"{card.get('id')} — {card.get('name')} — ")
			print(f"Rarity: {card.get('rarity')}")
	else:
		print("Card data could not be retrieved.")

if __name__ == "__main__":
    	main()
