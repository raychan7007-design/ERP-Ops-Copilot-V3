from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
KNOWLEDGE_DIR = ROOT / "knowledge"
DB_PATH = DATA_DIR / "erp_demo.db"
DEFAULT_TOP_K = 3
APP_VERSION = "v3"
APP_HOST = os.getenv("ERP_OPS_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("ERP_OPS_PORT", "8000"))
MAX_QUERY_LENGTH = int(os.getenv("ERP_OPS_MAX_QUERY_LENGTH", "1000"))
