"""All the SQL of the API. Routes call these functions and never write SQL themselves."""
import json


def list_regions(conn):
    """Every region, by name, with its shape as GeoJSON."""
    rows = conn.execute(
        "SELECT id, name, ST_AsGeoJSON(geom)::json FROM regions ORDER BY name"
    ).fetchall()
    return [{"id": id, "name": name, "geometry": geometry} for id, name, geometry in rows]


def create_region(conn, name, geometry):
    """Insert a region and return it. The database re-checks the name and the shape (CHECK constraints)."""
    row = conn.execute(
        """
        INSERT INTO regions (name, geom)
        VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
        RETURNING id, name, ST_AsGeoJSON(geom)::json
        """,
        (name, json.dumps(geometry)),
    ).fetchone()
    return {"id": row[0], "name": row[1], "geometry": row[2]}


def scenes_near(conn, lon, lat, meters, limit):
    rows = conn.execute(
        """
        WITH p AS (SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography AS geog)
        SELECT s.id, s.acquired_at, s.cloud_cover, s.cog_url,
               ST_Distance(s.footprint::geography, p.geog) AS metres_away
        FROM scenes s, p
        WHERE ST_DWithin(s.footprint::geography, p.geog, %s)
        ORDER BY metres_away, s.acquired_at DESC
        LIMIT %s
        """,
        (lon, lat, meters, limit),
    ).fetchall()
    return [{"id": id, "acquired_at": acquired_at, "cloud_cover": cloud_cover, "cog_url": cog_url, "metres_away": metres_away} for id, acquired_at, cloud_cover, cog_url, metres_away in rows]