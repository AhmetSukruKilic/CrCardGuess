import socket
from wsgiref import headers
import requests
import urllib3.util.connection as urllib3_connection
from api_settings import CR_API, BASE_URL
import socket
import requests

def _force_ipv4():
	def _family():
		return socket.AF_INET
	urllib3_connection.allowed_gai_family = _family

_force_ipv4()

def get_player(player_tag):
	if player_tag is None:
		raise ValueError("player_tag must be provided")

	if player_tag.startswith("#"):
		player_tag = player_tag.replace("#", "%23")

	after_fix = f'players/{player_tag}'

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

	after_fix = f'players/{player_tag}/battlelog'

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

	if battle_log:
		for battle in battle_log[:5]:
			print(f"Battle Type: {battle.get('type')} — ")
			print(f"Arena: {battle.get('arena', {}).get('name')}")

if __name__ == "__main__":
	main()
