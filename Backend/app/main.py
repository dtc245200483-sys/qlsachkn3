from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .routers import accounts, admin, auth, books, borrows, catalog, export, notifications, readers, requests, reservations, stats

app = FastAPI(
    title="Hệ thống quản lý thư viện - Backend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)
app.include_router(readers.router)
app.include_router(borrows.router)
app.include_router(requests.router)
app.include_router(accounts.router)
app.include_router(catalog.router)
app.include_router(reservations.router)
app.include_router(notifications.router)
app.include_router(stats.router)
app.include_router(export.router)
