import { TITILER_URL, DEFAULT_SCENE_URL } from "./config";
import type { View } from "./searchSlice";
import type { Scene } from "./types";

const CATALOG = "https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/";
const NDVI_FORMULA = "(b2-b1)/(b2+b1)"; // b1 = red, b2 = near-infrared, in the order of `assets`

// Titiler turns a Cloud Optimized GeoTIFF into map tiles on request.
// {z}/{x}/{y} stay as they are: MapLibre replaces them with the numbers of each tile it needs.
export function tileUrl(cogUrl: string): string {
  return `${TITILER_URL}/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.png?url=${encodeURIComponent(cogUrl)}`;
}

export function mapTilesUrl(scene: Scene | null, view: View): string {
  if (scene === null) {
    return tileUrl(DEFAULT_SCENE_URL);
  }
  if (view === "ndvi") {
    return ndviTileUrl(scene.id);
  }
  return tileUrl(scene.cog_url);
}

export function ndviTileUrl(sceneId: string): string {
  const scene = encodeURIComponent(CATALOG + sceneId);
  const formula = encodeURIComponent(NDVI_FORMULA);
  return (
    `${TITILER_URL}/stac/tiles/WebMercatorQuad/{z}/{x}/{y}.png` +
    `?url=${scene}&assets=red&assets=nir&expression=${formula}` +
    `&rescale=-1,1&colormap_name=rdylgn`
  );
}