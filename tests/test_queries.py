def test_coverage_is_the_share_of_the_region_a_scene_covers(conn, run_query):
    conn.execute(
        "INSERT INTO regions (name, geom) VALUES (%s, ST_MakeEnvelope(0, 0, 2, 2, 4326))",
        ("Test region",),
    )
    conn.execute(SCENE_SQL, ("west-half", "2026-01-01", 1, 0, 0, 1, 2, "https://example.com/a.tif"))
    conn.execute(SCENE_SQL, ("far-away", "2026-01-01", 1, 10, 10, 11, 11, "https://example.com/b.tif"))

    rows = run_query("02-coverage-of-region.sql", region="Test region")

    assert len(rows) == 1
    scene_id, day, covered_pct = rows[0]
    assert scene_id == "west-half"
    assert covered_pct == 50

SCENE_SQL = (
    "INSERT INTO scenes (id, acquired_at, cloud_cover, footprint, cog_url) "
    "VALUES (%s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, 4326), %s)"
)


def test_scenes_for_a_region_come_newest_first_and_skip_other_places(conn, run_query):
    conn.execute(
        "INSERT INTO regions (name, geom) VALUES (%s, ST_MakeEnvelope(0, 0, 2, 2, 4326))",
        ("Test region",),
    )
    url = "https://example.com/scene.tif"
    conn.execute(SCENE_SQL, ("older", "2026-01-01", 1, 0, 0, 1, 1, url))
    conn.execute(SCENE_SQL, ("newer", "2026-03-01", 1, 1, 1, 2, 2, url))
    conn.execute(SCENE_SQL, ("elsewhere", "2026-06-01", 1, 10, 10, 11, 11, url))

    rows = run_query("01-scenes-for-region.sql", region="Test region")

    assert [row[0] for row in rows] == ["newer", "older"]


def test_scenes_near_a_point_are_found_only_within_the_radius(run_query, conn):
    # The scene starts 1 degree of longitude east of the point, on the equator.
    # One degree there is about 111,319 metres.
    conn.execute(SCENE_SQL, ("east", "2026-01-01", 1, 1, 0, 2, 1, "https://example.com/e.tif"))

    too_small = run_query("03-scenes-near-point.sql", lon=0, lat=0, meters=100_000)
    big_enough = run_query("03-scenes-near-point.sql", lon=0, lat=0, meters=120_000)

    assert too_small == []
    assert len(big_enough) == 1
    scene_id, day, metres_away = big_enough[0]
    assert scene_id == "east"
    assert 111_000 < metres_away < 112_000
