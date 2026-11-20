from seed_scenes import to_row
import json


def test_to_row_picks_the_columns_in_table_order():
    geometry = {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]}
    item = {
        "id": "name1",
        "properties": {"datetime": "2026-10-15", "eo:cloud_cover": 12.5},
        "geometry": geometry,
        "assets": {"visual":{"href": "https://ex"}}
    }
    result = to_row(item)

    assert result == ("name1", "2026-10-15", 12.5, json.dumps(geometry), "https://ex")
