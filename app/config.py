from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY", "dev-key-change-me")
FMCSA_WEB_KEY = os.getenv("FMCSA_WEB_KEY", "")
HAPPYROBOT_API_KEY = os.getenv("HAPPYROBOT_API_KEY", "")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "carrier_sales.db")
