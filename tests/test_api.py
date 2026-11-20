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
