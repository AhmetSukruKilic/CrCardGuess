import os
import requests
import urllib3.util.connection as urllib3_connection
import socket

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

CR_API = os.getenv("CR_API")

HEADERS = {
    "Authorization": f"Bearer {CR_API}",
}

if not CR_API:
    raise RuntimeError("CR_API env var is missing. Set it in .env or your shell.")

CR_API = CR_API.strip().strip('"').strip("'").replace("\n", "").replace("\r", "")

BASE_URL = (os.getenv("CR_BASE_URL")).rstrip("/")

if not BASE_URL:
    raise RuntimeError("CR_BASE_URL env var is missing. Set it in .env or your shell.")


def health_check() -> bool:
    after_fix = "players/%23Q8PRJJ92"
    url = f"{BASE_URL}/{after_fix}"

    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        return True
    print("Health Check Error:", resp.status_code, resp.text[:300])
    print("Current IP:", requests.get("https://api.ipify.org").text)
    return False


def _force_ipv4():
    def _family():
        return socket.AF_INET

    urllib3_connection.allowed_gai_family = _family


_force_ipv4()


if __name__ == "__main__":
    if health_check():
        print("Health check passed. IP is authorized.")
    else:
        print("Health check failed. IP is not authorized.")
