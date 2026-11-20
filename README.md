# GeoLens

A small web map for exploring satellite imagery, built as a learning project. It serves real Sentinel-2 images of Chiba and Tokyo Bay as map tiles, keeps regions of interest and image footprints in PostGIS, and answers spatial questions about them, through a small FastAPI backend. A richer front end and a vegetation (NDVI) layer are planned.

This is a learning project, built with guidance from Claude Code. The assistant set up the boilerplate (Docker, CI, the test fixtures, the API skeleton), explained each concept and reviewed my work. I wrote the core pieces myself, some from skeletons with blanks to fill in: the schema constraints, the seed script's row mapping, the three spatial queries, the request model for creating a region, the two search functions of the API, and most of the tests.

## Status

Stage 3 of 5 is finished. This list shows only what is actually done.

- [x] Stage 1: Titiler serves map tiles from a real Sentinel-2 image (a Cloud Optimized GeoTIFF on AWS Open Data), shown on a MapLibre map
- [x] Stage 2: PostGIS holds regions of interest and image footprints, with spatial indexes
- [x] A seed script loads up to 100 real, mostly cloud-free scenes from the Earth Search catalog (safe to run twice)
- [x] Three spatial queries: scenes touching a region, how much of a region each scene covers (in square metres), and scenes within a distance of a point
- [x] Stage 3: a FastAPI backend with five endpoints: health check, list and create regions, scenes within a distance of a point, and the scenes that touch a region (with date and cloud filters and the share of the region each one covers)
- [x] 12 automated tests against a real PostGIS database: schema rules, the seed script's row mapping, the three queries, and six API tests (create and list a region, an out-of-range polygon, the cloud filter, the inclusive `to` date, the distance search, an unknown region)
- [x] CI: GitHub Actions starts a PostGIS service and runs the tests on every push, and fails if the database is missing instead of skipping the tests

Not done yet:

- [ ] Stage 4: a Next.js and TypeScript front end with Redux Toolkit. It will also need two changes to the API: CORS (a browser page on another port cannot call it today) and running it from `docker-compose.yml` (today you start it with `uvicorn`).
- [ ] Stage 5: an NDVI layer computed with band math
- [ ] The map page does not read from the API yet.
- [ ] No tests for the web page.

Left out on purpose, to keep the project small: updating or deleting regions, authentication, and pagination (results are limited by a capped `limit`).

## Requirements

- Docker with Docker Compose
- Python 3.12 (for the seed script and the tests)
- An internet connection: the imagery is read from AWS, the seed script calls the Earth Search catalog, and the page loads MapLibre from a CDN (unpkg)

## Run

```sh
docker compose up -d --wait
```

Then open <http://localhost:8080>. You should see Chiba and Tokyo Bay from a Sentinel-2 pass on 16 January 2026.

- The first tiles take a few seconds, because Titiler reads them live from AWS in Oregon.
- The white areas are outside the satellite's path.
- The image only has data between zoom levels 8 and 14.

Stop it with `docker compose down`. Your data stays in the `pgdata` volume. `docker compose down -v` deletes it (see the notes on init scripts below).

### Load scenes and run the queries

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/seed_scenes.py
```

The database is published on `localhost:5433` (not 5432, to avoid clashing with a Postgres you may already run). Run a query with `psql` inside the container:

```sh
docker compose exec -T db psql -U geolens -d geolens -v region='Chiba city' < db/queries/01-scenes-for-region.sql
docker compose exec -T db psql -U geolens -d geolens -v region='Tokyo Bay' < db/queries/02-coverage-of-region.sql
docker compose exec -T db psql -U geolens -d geolens -v lon=141.6 -v lat=35.6 -v meters=50000 < db/queries/03-scenes-near-point.sql
```

The three sample regions are Chiba city, Tokyo Bay and Narita area.

### Run the API

With the database up and the scenes loaded:

```sh
.venv/bin/uvicorn api.main:app --port 8001 --reload
```

Port 8001 avoids Titiler, which uses 8000. Open <http://localhost:8001/docs> for an interactive page generated from the code. The API refuses to start if it cannot reach the database. To use another database, set `DATABASE_URL` (see `.env.example`).

| Endpoint | What it does |
|---|---|
| `GET /health` | Checks that the API can reach the database |
| `GET /regions` | Lists the regions, with their shapes as GeoJSON |
| `POST /regions` | Creates a region from `{"name": ..., "geometry": <GeoJSON Polygon>}` |
| `GET /regions/{id}/scenes` | Scenes touching a region, newest first, with `covered_pct`. Optional `from`, `to` (dates), `max_cloud` (0 to 100) and `limit` (1 to 100, default 10) |
| `GET /scenes/near` | Scenes within `meters` (up to 500,000) of `lon` and `lat`, nearest first, with `metres_away`. Optional `limit` |

Invalid input gets a `422` that names the field. An unknown region gets a `404`.

```sh
curl "localhost:8001/scenes/near?lon=141.6&lat=35.6&meters=50000&limit=3"
```

### Test

```sh
.venv/bin/python -m pytest -q
```

The tests need the database from `docker compose up`. They create and drop their own database, `geolens_test`, so they never touch your scenes. Without a database they are skipped locally, and fail when `REQUIRE_DB=1` is set (as CI does).

## How it works

```
Sentinel-2 image (a COG on AWS Open Data)
        |  Titiler reads only the byte ranges it needs
        v
Titiler (Docker, port 8000)  --- PNG map tiles --->  MapLibre in the browser (nginx, port 8080)

Earth Search catalog --- seed script (Python) ---> PostGIS (Docker, port 5433)
                                                    regions + scenes, spatial queries
                                                          ^
                                                          |  SQL with %s parameters
                                                    FastAPI (uvicorn, port 8001)
```

- **Cloud Optimized GeoTIFF (COG):** a GeoTIFF arranged in blocks, with smaller overview copies, so a program can read just one area over HTTP.
- **Dynamic tiling:** Titiler cuts each map tile when the browser asks for it, instead of storing pre-made tiles. That needs no storage and will also allow computing NDVI later. The cost is some CPU per tile and a slower first tile.

## Design decisions (Stage 2)

- **Coordinates are stored as longitude/latitude (EPSG:4326)** and converted to `geography` only when a query needs metres. That keeps one storage format that works anywhere in the world. Storing in a metric projection would make area and distance simple, but only inside one zone (for Kanto, Japan Plane Rectangular zone IX, EPSG:6677).
- **Datums:** the Japanese standard JGD2011 and WGS 84 differ by well under a metre. The Sentinel-2 pixels are 10 m wide, so the difference does not matter here and I do not convert between them.
- **The distance query needs its own index.** Casting a column to `geography` inside a query hides the ordinary spatial index, and so does comparing `ST_Distance(...) < n`. The fix is an index on the cast itself (`scenes_footprint_geog_gist`) and `ST_DWithin` in the query. In a one-off check on a scratch database with 50,000 generated scenes (not a benchmark suite), the unindexed form took about 716 ms and the indexed form about 10 ms. The cost is an extra index of a few MB and a slightly slower insert.
- **Init scripts run only once.** The files in `db/init/` run when the database volume is empty. After changing one, run `docker compose down -v` (this deletes the data, then run the seed script again). A failing init script makes the container exit, so check `docker compose logs db`.
- **A custom database image.** The usual `postgis/postgis` image is Intel-only, so `db/Dockerfile` builds PostGIS on top of the official Postgres image. CI runs on Intel and uses the prebuilt image.
- **Tests use a real database, not mocks.** The bugs that matter here (longitude/latitude order, polygon validity, metres vs degrees) live in the SQL. The query files are run by the tests exactly as shipped.

## Design decisions (Stage 3)

- **Sync endpoints, not async.** Each request spends its time waiting for PostGIS, and the connection pool (at most 10 connections) limits how many queries run at once. Async would move the queue from threads to an event loop without removing it. It would become the better choice if the API called slow outside services, such as Titiler or the catalog, on every request. I have not measured this; it is a reasoned choice.
- **Plain SQL in one module (`api/repository.py`), no ORM.** The SQL is the valuable part of this project, so it stays visible. Routes know nothing about SQL, and the SQL knows nothing about HTTP. The cost is mapping rows to dicts by hand.
- **Validation in two layers.** Pydantic checks the shape of the JSON (a Polygon, points with exactly two numbers inside the valid longitude and latitude range, a non-empty name). The database CHECK constraints check the geometry itself (a self-crossing polygon is rejected) and are the last line of defence. The API turns a rejected insert into a `422`.
- **The connection is a dependency.** Routes ask for it with `Depends(get_conn)`, so the tests can replace it with a rolled-back connection to the test database without changing any route.
- **Input limits protect the database.** The search radius is capped at 500 km and `limit` at 100. The values are my own choice, not measured.
- **Dynamic filters use parameters.** The `WHERE` of the region search is built from fixed text fragments, and every client value goes in as a `%s` parameter. Dates are compared against the raw column (not `acquired_at::date`) so the index on `acquired_at` stays usable. The `to` date is inclusive.
- **An unknown region is a `404`; a region with no matching scenes is `200` with an empty list.**

## Data and licenses

- **Imagery:** Sentinel-2 L2A scenes from AWS Open Data, found through the Earth Search catalog. Free to use, no account needed. Contains modified Copernicus Sentinel data 2025–2026.
- **Software:** [Titiler](https://github.com/developmentseed/titiler) (MIT) and [MapLibre GL JS](https://maplibre.org/) (BSD-3-Clause), PostgreSQL and PostGIS, FastAPI, Uvicorn, psycopg and pytest, all used as published. Versions are pinned in `docker-compose.yml`, `db/Dockerfile`, `web/index.html`, `requirements.txt` and `requirements-dev.txt`.
- **Credentials:** the database user and password in `docker-compose.yml` and `.env.example` are throwaway values for local development, not real secrets.

## Project layout

```
docker-compose.yml  Titiler, nginx and the PostGIS database
db/Dockerfile       PostGIS on the official Postgres image
db/init/            extension, schema, sample regions (run once on an empty volume)
db/queries/         the three spatial queries
scripts/            the seed script
api/                the FastAPI app: routes (main.py), SQL (repository.py), models (schemas.py), connection pool (db.py)
tests/              pytest tests against a real PostGIS database
web/                the map page: index.html and map.js
```

## License

MIT. See [LICENSE](LICENSE). The imagery and the libraries above have their own terms.
