"use client";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef, useState } from "react";

import { tileUrl } from "../lib/titiler";
import type { Region } from "../lib/types";
import { syncRegions } from "../lib/regionsLayer";

type Props = {
  regions: Region[];
  sceneUrl: string;
};

export default function MapView({ regions, sceneUrl }: Props) {
  // The map is a live object with methods and WebGL, so it lives in a ref, not in state
  // (and, later, never in Redux).
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [ready, setReady] = useState(false);

  // Effect 1: create the map once, remove it when the component goes away.
  // In development React mounts every component twice to expose missing cleanup:
  // without map.remove() there would be two maps.
  useEffect(() => {
    const map = new maplibregl.Map({
      container: containerRef.current!,
      center: [140.1, 35.6], // [longitude, latitude]: Chiba
      zoom: 9,
      style: {
        version: 8,
        sources: {
          satellite: {
            type: "raster",
            tiles: [tileUrl(sceneUrl)],
            tileSize: 256,
            minzoom: 8, // the image only exists between zoom 8 and 14
            maxzoom: 14,
            attribution: "Contains modified Copernicus Sentinel data 2026",
          },
        },
        layers: [{ id: "satellite", type: "raster", source: "satellite" }],
      },
    });
    map.addControl(new maplibregl.NavigationControl());
    map.on("load", () => setReady(true));
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
      setReady(false);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Effect 2: keep the regions on the map in sync with the regions we were given.
  // It runs when the map becomes ready and again whenever `regions` changes.
  useEffect(() => {
    if (!ready || !mapRef.current) return;
    syncRegions(mapRef.current, regions);
  }, [ready, regions]);

  // Effect 3: keeps the satellite image in sync with the selected scene's URL, and effect 1 uses it only for the first image
  useEffect(() => {
    if (!ready || !mapRef.current) return;
    const source = mapRef.current.getSource("satellite") as maplibregl.RasterTileSource | undefined;
    source?.setTiles([tileUrl(sceneUrl)]);
  }, [ready, sceneUrl]);

  return <div ref={containerRef} style={{ width: "100vw", height: "100vh" }} />;
}
