import os
try:
	from dotenv import load_dotenv
	load_dotenv()
except Exception:
    	pass

CR_API = os.getenv("CR_API")
if not CR_API:
    	raise RuntimeError("CR_API env var is missing. Set it in .env or your shell.")

CR_API = CR_API.strip().strip('"').strip("'").replace("\n", "").replace("\r", "")

BASE_URL = (os.getenv("CR_BASE_URL")).rstrip("/")

if not BASE_URL:
    	raise RuntimeError("CR_BASE_URL env var is missing. Set it in .env or your shell.")