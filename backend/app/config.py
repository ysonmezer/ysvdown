import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")
load_dotenv()


class Settings:
    api_token: str = os.getenv("API_TOKEN", "change-me")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    download_dir: Path = Path(os.getenv("DOWNLOAD_DIR", "downloads")).resolve()
    file_ttl_hours: int = int(os.getenv("FILE_TTL_HOURS", "24"))
    max_concurrent_jobs: int = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")


settings = Settings()
settings.download_dir.mkdir(parents=True, exist_ok=True)
