"""Load recent Sentinel-2 scenes around Chiba from the Earth Search catalog into PostGIS.

Run from the project folder, with the database up (docker compose up -d --wait db):
    .venv/bin/python scripts/seed_scenes.py

It is safe to run again: a scene that is already in the table is skipped.
"""
import json
import os
import urllib.request

import psycopg

STAC_SEARCH = "https://earth-search.aws.element84.com/v1/search"

# The same local-development value as docker-compose.yml and .env.example.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://geolens:geolens@localhost:5433/geolens")


def fetch_scenes():
    """Ask the catalog for up to 100 mostly cloud-free scenes around Chiba, as a list of dicts."""
    query = {
        "collections": ["sentinel-2-l2a"],
        "bbox": [139.6, 35.2, 140.5, 35.9],  # [west, south, east, north] in lon/lat
        "datetime": "2025-11-01T00:00:00Z/2026-11-15T00:00:00Z",
        "query": {"eo:cloud_cover": {"lt": 20}},
        "limit": 100,
    }
    request = urllib.request.Request(
        STAC_SEARCH,
        data=json.dumps(query).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["features"]


def to_row(item):
    """Turn one catalog item (a dict) into the values for one row of the scenes table."""
    return (
        item["id"],
        item["properties"]["datetime"],
        item["properties"]["eo:cloud_cover"],
        json.dumps(item["geometry"]),
        item["assets"]["visual"]["href"]
    )


def insert(conn, rows):
    """Save the rows into the scenes table, skipping scenes that are already there.

    Returns how many rows were new.
    """
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO scenes (id, acquired_at, cloud_cover, footprint, cog_url)
            VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s)
            ON CONFLICT (id) DO NOTHING
            """,
            rows,
        )
        return cur.rowcount


def main():
    items = fetch_scenes()
    rows = [to_row(item) for item in items]
    with psycopg.connect(DATABASE_URL) as conn:
        added = insert(conn, rows)
    print(f"The catalog returned {len(rows)} scenes; {added} were new.")


if __name__ == "__main__":
    main()
