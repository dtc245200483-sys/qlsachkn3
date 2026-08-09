import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

STATIC_DIR = os.path.join(BASE_DIR, "static")
AVATAR_DIR = os.path.join(STATIC_DIR, "avatars")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://@localhost\\QUANGHUNG/LibraryDB"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    "&TrustServerCertificate=yes",
)
DB_NAME = os.getenv("DB_NAME", "LibraryDB")
DB_SERVER = os.getenv("DB_SERVER", "localhost\\QUANGHUNG")
ODBC_DRIVER = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
BACKUP_DIR = os.getenv("BACKUP_DIR", "")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
