import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() in {"1", "true", "yes"}
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./namonexus.db")
    AUTO_CREATE_DB = os.getenv("AUTO_CREATE_DB", "false").lower() in {"1", "true", "yes"}
    CRITICAL_KEYWORDS = [
        "kill myself",
        "end it all",
        "hurt myself",
        "can't go on",
        "no reason to live",
    ]
    MAX_MEMORY_ITEMS = int(os.getenv("MAX_MEMORY_ITEMS", "1000"))
    MEMORY_RETENTION_DAYS = int(os.getenv("MEMORY_RETENTION_DAYS", "365"))


config = Config()
