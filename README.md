# GeoLens

A small web map for exploring satellite imagery, built as a learning project. It serves real Sentinel-2 images of Chiba and Tokyo Bay as map tiles, with the aim of adding regions of interest, an image search and a vegetation (NDVI) layer.

## Status

Stage 1 of 5 is finished. This list shows only what is actually done.

- [x] Titiler serves map tiles from one real Sentinel-2 image (a Cloud Optimized GeoTIFF on AWS Open Data), read over HTTP without downloading the whole file
- [x] A web page shows those tiles on a MapLibre map, with zoom and pan
- [x] Everything starts with one `docker compose up`

Not done yet:

- [ ] Stage 2: PostGIS for regions of interest and image footprints, with spatial queries
- [ ] Stage 3: a FastAPI backend to manage regions and search the image catalog
- [ ] Stage 4: a Next.js and TypeScript front end with Redux Toolkit
- [ ] Stage 5: an NDVI layer computed with band math
- [ ] Tests and CI. Stage 1 has no logic of its own to test, so there are none yet.

## Requirements

- Docker with Docker Compose
- An internet connection: the imagery is read from AWS, and the page loads MapLibre from a CDN (unpkg)

## Run

```sh
docker compose up -d
```

Then open <http://localhost:8080>. You should see Chiba and Tokyo Bay from a Sentinel-2 pass on 16 January 2026.

- The first tiles take a few seconds, because Titiler reads them live from AWS in Oregon. Tiles that were already requested appear faster.
- The white areas are outside the satellite's path. The slanted edge on the right is the edge of that path.
- The image only has data between zoom levels 8 and 14.

Stop it with `docker compose down`.

## How it works

```
Sentinel-2 image (a COG on AWS Open Data)
        |  Titiler reads only the byte ranges it needs
        v
Titiler (Docker, port 8000)  --- PNG map tiles --->  MapLibre in the browser (nginx, port 8080)
```

- **Cloud Optimized GeoTIFF (COG):** a GeoTIFF arranged in blocks, with smaller overview copies, so a program can read just one area over HTTP. The image used here is about 10,980 by 10,980 pixels.
- **Dynamic tiling:** Titiler cuts each map tile when the browser asks for it, instead of storing pre-made tiles. That needs no storage and works with any image, and it will also allow computing NDVI later. The cost is some CPU per tile and a slower first tile.
- **Coordinate systems:** the image is stored in EPSG:32654 (UTM zone 54N). Web maps use EPSG:3857 (Web Mercator), so Titiler reprojects each tile on the fly.

## Data and licenses

- **Imagery:** Sentinel-2 L2A scene `S2B_54SVE_20260116_0_L2A`, from AWS Open Data (found through the Earth Search catalog). It is free to use and needs no account. Contains modified Copernicus Sentinel data 2026.
- **Software:** [Titiler](https://github.com/developmentseed/titiler) (MIT) and [MapLibre GL JS](https://maplibre.org/) (BSD-3-Clause), both used as published. Their versions are pinned in `docker-compose.yml` and `web/index.html`.

## Project layout

```
docker-compose.yml  Titiler (tile server) and nginx (serves the page)
web/                the map page: index.html and map.js
```

## License

MIT. See [LICENSE](LICENSE). The imagery and the libraries above have their own terms.
