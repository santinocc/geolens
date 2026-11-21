"use client";

import MapView from "../components/MapView";
import { DEFAULT_SCENE_URL } from "../lib/config";
import { useGetRegionsQuery } from "../lib/api";
import type { Region } from "../lib/types";

// One stable empty array. Writing `data = []` inline would create a new array on every render,
// and MapView's effect (which depends on `regions`) would then run on every render.
const NO_REGIONS: Region[] = [];

export default function Home() {
  const { data, isError } = useGetRegionsQuery();

  return (
    <>
      <MapView regions={data ?? NO_REGIONS} sceneUrl={DEFAULT_SCENE_URL} />
      {isError && (
        <p style={{ position: "absolute", top: 8, left: 8, margin: 0, padding: "4px 8px", background: "white" }}>
          Could not load the regions. Is the API running?
        </p>
      )}
    </>
  );
}
