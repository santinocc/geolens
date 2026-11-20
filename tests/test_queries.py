def test_coverage_is_the_share_of_the_region_a_scene_covers(conn, run_query):
    conn.execute(
        "INSERT INTO regions (name, geom) VALUES (%s, ST_MakeEnvelope(0, 0, 2, 2, 4326))",
        ("Test region",),
    )
    scene_sql = (
        "INSERT INTO scenes (id, acquired_at, cloud_cover, footprint, cog_url) "
        "VALUES (%s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, 4326), %s)"
    )
    conn.execute(scene_sql, ("west-half", "2026-01-01", 1, 0, 0, 1, 2, "https://example.com/a.tif"))
    conn.execute(scene_sql, ("far-away", "2026-01-01", 1, 10, 10, 11, 11, "https://example.com/b.tif"))

    rows = run_query("02-coverage-of-region.sql", region="Test region")

    assert len(rows) == 1
    scene_id, day, covered_pct = rows[0]
    assert scene_id == "west-half"
    assert covered_pct == 50