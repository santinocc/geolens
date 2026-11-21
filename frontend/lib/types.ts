// The shapes the API sends. They mirror api/schemas.py.
import type { Polygon } from "geojson";

export type Region = {
  id: string;
  name: string;
  geometry: Polygon;
};
