# GeoLens

A small web map for exploring satellite imagery, built as a learning project. It serves real Sentinel-2 images of Chiba and Tokyo Bay as map tiles, keeps regions of interest and image footprints in PostGIS, and answers spatial questions about them. A search API, a richer front end and a vegetation (NDVI) layer are planned.

This is a learning project, built with guidance from Claude Code. The assistant set up the boilerplate (Docker, CI, the test fixtures), explained each concept and reviewed my work. I wrote the core pieces myself, some from skeletons with blanks to fill in: the schema constraints, the seed script's row mapping, the three spatial queries and most of the tests.

## Status

Stage 2 of 5 is finished. This list shows only what is actually done.

- [x] Stage 1: Titiler serves map tiles from a real Sentinel-2 image (a Cloud Optimized GeoTIFF on AWS Open Data), shown on a MapLibre map
- [x] Stage 2: PostGIS holds regions of interest and image footprints, with spatial indexes
- [x] A seed script loads up to 100 real, mostly cloud-free scenes from the Earth Search catalog (safe to run twice)
- [x] Three spatial queries: scenes touching a region, how much of a region each scene covers (in square metres), and scenes within a distance of a point
- [x] 6 automated tests against a real PostGIS database: schema rules, the seed script's row mapping, and the three queries

Not done yet:

- [ ] CI: a GitHub Actions workflow is written (`.github/workflows/ci.yml`) but has not run yet, so I do not claim it works until it does
- [ ] Stage 3: a FastAPI backend to manage regions and search the image catalog
- [ ] Stage 4: a Next.js and TypeScript front end with Redux Toolkit
- [ ] Stage 5: an NDVI layer computed with band math
- [ ] The map page does not read from the database yet. The database and the map are separate until Stage 3 and 4.
- [ ] No tests for the web page.

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

## Data and licenses

- **Imagery:** Sentinel-2 L2A scenes from AWS Open Data, found through the Earth Search catalog. Free to use, no account needed. Contains modified Copernicus Sentinel data 2025–2026.
- **Software:** [Titiler](https://github.com/developmentseed/titiler) (MIT) and [MapLibre GL JS](https://maplibre.org/) (BSD-3-Clause), PostgreSQL and PostGIS, all used as published. Versions are pinned in `docker-compose.yml`, `db/Dockerfile` and `web/index.html`.
- **Credentials:** the database user and password in `docker-compose.yml` and `.env.example` are throwaway values for local development, not real secrets.

## Project layout

```
docker-compose.yml  Titiler, nginx and the PostGIS database
db/Dockerfile       PostGIS on the official Postgres image
db/init/            extension, schema, sample regions (run once on an empty volume)
db/queries/         the three spatial queries
scripts/            the seed script
tests/              pytest tests against a real PostGIS database
web/                the map page: index.html and map.js
```

## License

MIT. See [LICENSE](LICENSE). The imagery and the libraries above have their own terms.
