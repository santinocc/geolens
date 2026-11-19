// The Sentinel-2 image: a Cloud Optimized GeoTIFF on AWS Open Data (public, free).
const IMAGE_URL =
  'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/54/S/VE/2026/1/S2B_54SVE_20260116_0_L2A/TCI.tif';

// Titiler, started by docker-compose.yml.
const TITILER = 'http://localhost:8000';

// Titiler turns the image into map tiles on request. {z}/{x}/{y} stay as they are:
// MapLibre replaces them with the numbers of each tile it needs.
const tileUrl =
  `${TITILER}/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.png?url=${encodeURIComponent(IMAGE_URL)}`;

const map = new maplibregl.Map({
  container: 'map',
  center: [140.1, 35.6], // [longitude, latitude]: Chiba
  zoom: 9,
  style: {
    version: 8,
    sources: {
      satellite: {
        type: 'raster',
        tiles: [tileUrl],
        tileSize: 256,
        // The image only exists between zoom 8 and 14.
        minzoom: 8,
        maxzoom: 14,
        attribution: 'Contains modified Copernicus Sentinel data 2026',
      },
    },
    layers: [
      { id: 'satellite', type: 'raster', source: 'satellite' }
    ],
  },
});

map.addControl(new maplibregl.NavigationControl());
