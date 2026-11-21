import { TITILER_URL } from "./config";

// Titiler turns a Cloud Optimized GeoTIFF into map tiles on request.
// {z}/{x}/{y} stay as they are: MapLibre replaces them with the numbers of each tile it needs.
export function tileUrl(cogUrl: string): string {
  return `${TITILER_URL}/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.png?url=${encodeURIComponent(cogUrl)}`;
}
