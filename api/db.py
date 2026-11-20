"""Database access for the API: one connection pool, and a way for each request to borrow from it."""
import os

from fastapi import Request
from psycopg_pool import ConnectionPool

# The same local-development value as docker-compose.yml and .env.example.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://geolens:geolens@localhost:5433/geolens")


def open_pool(url=DATABASE_URL):
    """Open a pool of connections. Raises at startup if the database is unreachable (fail fast)."""
    pool = ConnectionPool(url, min_size=1, max_size=10, open=False)
    pool.open(wait=True, timeout=10)
    return pool


def get_conn(request: Request):
    """FastAPI dependency: lend one connection to a request, then give it back.

    The connection commits when the request succeeds and rolls back if it raises.
    Tests replace this function to point the API at the test database.
    """
    with request.app.state.pool.connection() as conn:
        yield conn
