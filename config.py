import os
from dataclasses import dataclass

@dataclass
class Config:
    """Sozlamar"""
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "TOKEN_YO'Q")
    GITGUB_API_URL: str = "https://api.github.com"
    MAX_REPOS_DISPLAY: int = 10

    #malumotlar bazasi sekretlari
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "MA'LUMOTLAR BAZASI URLSI")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "MA'lumotlar bazasi kaliti")

    #shifr kaliti
    ENCRYPRION_KEY = os.getenv("ENCRYPTION_KEY")

config = Config()