"""The database itself must refuse bad data, whatever code is talking to it."""
import psycopg
import pytest


def test_region_with_a_self_crossing_polygon_is_rejected(conn):
    # A "bow tie": the edges cross each other, so it is not a valid polygon.
    bow_tie = "POLYGON((0 0, 2 2, 2 0, 0 2, 0 0))"

    # The insert must fail. The error type says which kind of rule was broken,
    # and the constraint name says which rule: that is what makes the test precise.
    with pytest.raises(psycopg.errors.CheckViolation) as error:
        conn.execute(
            "INSERT INTO regions (name, geom) VALUES (%s, ST_GeomFromText(%s, 4326))",
            ("Bow tie", bow_tie),
        )

    assert error.value.diag.constraint_name == "regions_geom_valid"


def test_scene_with_a_cloud_cover_101_is_rejected(conn):
    with pytest.raises(psycopg.errors.CheckViolation) as error:
        conn.execute(
            "INSERT INTO scenes (id, acquired_at, cloud_cover, footprint, cog_url) VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s)",
            ("txt1", "2026-01-16", 101, "POLYGON((0 0, 2 0, 2 2, 0 2, 0 0))", "https://txt2"),
        )

    assert error.value.diag.constraint_name == "scenes_cloud_cover_check"
    