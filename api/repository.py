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
