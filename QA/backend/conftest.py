import time

import httpx
import pytest

BASE_URL = "http://127.0.0.1:8001"
PASSWORD = "Test@12345"


def login(client: httpx.Client, username: str) -> str:
    resp = client.post(
        "/api/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


def unique(prefix: str) -> str:
    return f"{prefix}{time.time_ns() % 100000000:08d}"


@pytest.fixture(scope="session")
def client() -> httpx.Client:
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


@pytest.fixture(scope="session")
def tokens(client: httpx.Client) -> dict:
    return {
        "admin": login(client, "qa_admin"),
        "librarian": login(client, "qa_librarian"),
        "reader1": login(client, "qa_reader1"),
        "reader2": login(client, "qa_reader2"),
    }


@pytest.fixture()
def headers(tokens: dict):
    def _make(role: str) -> dict:
        return {"Authorization": f"Bearer {tokens[role]}"}

    return _make
