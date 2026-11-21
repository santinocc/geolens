// The shapes the API sends. They mirror api/schemas.py.
import type { Polygon } from "geojson";

export type Region = {
  id: string;
  name: string;
  geometry: Polygon;
};

export type Scene = {
  id: string;
  acquired_at: string;
  cloud_cover: number;
  cog_url: string;
  metres_away: number | null;
  covered_pct: number | null;
};