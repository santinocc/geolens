"""All the SQL of the API. Routes call these functions and never write SQL themselves."""
import json
from datetime import timedelta


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


def region_exists(conn, region_id):
    """True if a region with this id exists."""
    return conn.execute("SELECT 1 FROM regions WHERE id = %s", (region_id,)).fetchone() is not None


def scenes_for_region(conn, region_id, date_from, date_to, max_cloud, limit):
    conditions = ["r.id = %s"]
    params = [region_id]
    if date_from is not None:
        conditions.append("s.acquired_at >= %s")
        params.append(date_from)
    if date_to is not None:
        conditions.append("s.acquired_at < %s")
        params.append(date_to + timedelta(days=1))
    if max_cloud is not None:
        conditions.append("s.cloud_cover <= %s")
        params.append(max_cloud)
    params.append(limit)
    where = " AND ".join(conditions)
    rows = conn.execute(
        f"""
        SELECT s.id, s.acquired_at, s.cloud_cover, s.cog_url,
               round((100 * ST_Area(ST_Intersection(s.footprint, r.geom)::geography)
                          / ST_Area(r.geom::geography))::numeric, 1)
        FROM scenes s
        JOIN regions r ON ST_Intersects(s.footprint, r.geom)
        WHERE {where}
        ORDER BY s.acquired_at DESC
        LIMIT %s
        """,
        params,
    ).fetchall()
    return [{"id": id, "acquired_at": acquired_at, "cloud_cover": cloud_cover, "cog_url": cog_url, "covered_pct": covered_pct} for id, acquired_at, cloud_cover, cog_url, covered_pct in rows]