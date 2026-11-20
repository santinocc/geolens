SQUARE = {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]}
SCENE_SQL = (
    "INSERT INTO scenes (id, acquired_at, cloud_cover, footprint, cog_url) "
    "VALUES (%s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, 4326), %s)"
)

def test_a_created_region_is_returned_and_then_listed(client):
    created = client.post("/regions", json={"name": "Test region", "geometry": SQUARE})

    assert created.status_code == 201
    assert created.json()["name"] == "Test region"

    listed = client.get("/regions")

    assert "Test region" in [region["name"] for region in listed.json()]


def test_max_cloud_keeps_only_the_clearer_scenes(client, conn):
    region_id = conn.execute(
        "INSERT INTO regions (name, geom) VALUES (%s, ST_MakeEnvelope(0, 0, 2, 2, 4326)) RETURNING id",
        ("Test region",),
    ).fetchone()[0]
    url = "https://example.com/scene.tif"
    conn.execute(SCENE_SQL, ("clear", "2026-01-01", 1, 0, 0, 2, 2, url))
    conn.execute(SCENE_SQL, ("cloudy", "2026-01-02", 50, 0, 0, 2, 2, url))

    # your part: call the endpoint, then check the status and which scenes came back
    response = client.get(f"/regions/{region_id}/scenes", params={"max_cloud": 10})
    assert response.status_code == 200
    assert [scene["id"] for scene in response.json()] == ["clear"]


def test_an_unknown_region_gives_a_404(client):
    response = client.get("/regions/00000000-0000-0000-0000-000000000000/scenes")
    assert response.status_code == 404


def insert_region(conn):
    """A 2 x 2 degree region and its id."""
    return conn.execute(
        "INSERT INTO regions (name, geom) VALUES (%s, ST_MakeEnvelope(0, 0, 2, 2, 4326)) RETURNING id",
        ("Test region",),
    ).fetchone()[0]


def test_a_region_outside_the_valid_longitude_and_latitude_is_rejected(client):
    off_the_map = {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [2, 95], [0, 95], [0, 0]]]}

    response = client.post("/regions", json={"name": "Too far north", "geometry": off_the_map})

    assert response.status_code == 422


def test_scenes_near_a_point_come_nearest_first_with_their_distance(client, conn):
    # One scene starts 1 degree of longitude east of the point, on the equator: about 111,319 m.
    conn.execute(SCENE_SQL, ("east", "2026-01-01", 1, 1, 0, 2, 1, "https://example.com/e.tif"))

    too_small = client.get("/scenes/near", params={"lon": 0, "lat": 0, "meters": 100_000})
    big_enough = client.get("/scenes/near", params={"lon": 0, "lat": 0, "meters": 120_000})

    assert too_small.json() == []
    assert [scene["id"] for scene in big_enough.json()] == ["east"]
    assert 111_000 < big_enough.json()[0]["metres_away"] < 112_000


def test_the_to_date_includes_scenes_from_that_whole_day(client, conn):
    region_id = insert_region(conn)
    conn.execute(SCENE_SQL, ("afternoon", "2026-01-31 15:00", 1, 0, 0, 2, 2, "https://example.com/a.tif"))

    on_the_day = client.get(f"/regions/{region_id}/scenes", params={"to": "2026-01-31"})
    the_day_before = client.get(f"/regions/{region_id}/scenes", params={"to": "2026-01-30"})

    assert [scene["id"] for scene in on_the_day.json()] == ["afternoon"]
    assert the_day_before.json() == []
