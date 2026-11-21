import type { FeatureCollection } from "geojson";
import type { GeoJSONSource, Map } from "maplibre-gl";
import type { Region } from "./types";

export function syncRegions(map: Map, regions: Region[]) {
  const data: FeatureCollection = {
    type: "FeatureCollection",
    features: regions.map((region) => ({
      type: "Feature",
      properties: { name: region.name },
      geometry: region.geometry,
    })),
  };

  const source = map.getSource("regions") as GeoJSONSource | undefined;
  if (source) {
    source.setData(data);
    return;
  }

  map.addSource("regions", { type: "geojson", data });
  map.addLayer({
    id: "regions-fill",
    type: "fill",
    source: "regions",
    paint: { "fill-color": "#e11d48", "fill-opacity": 0.2 },
  });
  map.addLayer({
    id: "regions-outline",
    type: "line",
    source: "regions",
    paint: { "line-color": "#e11d48", "line-width": 2 },
  });
}