"""Test setup: a throwaway PostGIS database built from the project's own init scripts.

The tests never touch the development database. A session fixture drops and recreates
a database called geolens_test, then runs db/init/*.sql in order, so the tests see
exactly the schema that `docker compose up` creates.
"""
import os
import re
from pathlib import Path

import psycopg
import pytest
from psycopg.conninfo import make_conninfo

# Same local-development value as docker-compose.yml and .env.example.
ADMIN_URL = os.environ.get("DATABASE_URL", "postgres://geolens:geolens@localhost:5433/geolens")
TEST_DB = "geolens_test"
INIT_DIR = Path(__file__).resolve().parent.parent / "db" / "init"


def _unavailable(reason):
    """In CI (REQUIRE_DB=1) a missing database is a failure; on a laptop it is a skip."""
    if os.environ.get("REQUIRE_DB") == "1":
        pytest.fail(reason)
    pytest.skip(reason)


@pytest.fixture(scope="session")
def test_db_url():
    try:
        admin = psycopg.connect(ADMIN_URL, autocommit=True, connect_timeout=5)
    except psycopg.OperationalError as error:
        _unavailable(f"PostGIS is not reachable ({error}). Run: docker compose up -d --wait db")
    with admin:
        admin.execute(f'DROP DATABASE IF EXISTS "{TEST_DB}" WITH (FORCE)')
        admin.execute(f'CREATE DATABASE "{TEST_DB}"')
    url = make_conninfo(ADMIN_URL, dbname=TEST_DB)
    with psycopg.connect(url, autocommit=True) as setup:
        for script in sorted(INIT_DIR.glob("*.sql")):
            setup.execute(script.read_text())
    return url


@pytest.fixture
def conn(test_db_url):
    """A connection whose changes are rolled back after each test."""
    with psycopg.connect(test_db_url) as connection:
        yield connection
        connection.rollback()


QUERIES_DIR = Path(__file__).resolve().parent.parent / "db" / "queries"


@pytest.fixture
def run_query(conn):
    """Run one of the db/queries/*.sql files and return its rows.

    The files use psql variables (:'region', :lon). psycopg does not know that syntax, so
    this turns each one into a real parameter. A cast such as ::geography is left alone.
    """
    def run(filename, **params):
        sql = (QUERIES_DIR / filename).read_text()
        sql = sql.replace("%", "%%")                    # a literal % (even in a comment) must be doubled
        sql = re.sub(r":'(\w+)'", r"%(\1)s", sql)       # :'region' -> %(region)s
        sql = re.sub(r"(?<!:):([a-z_]\w*)", r"%(\1)s", sql)  # :lon -> %(lon)s
        return conn.execute(sql, params).fetchall()
    return run
