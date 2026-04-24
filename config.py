# config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_PREFIX = "/api/v0/ai"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET")
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")