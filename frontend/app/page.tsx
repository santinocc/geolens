"use client";

import FilterForm from "../components/FilterForm";
import MapView from "../components/MapView";
import RegionPicker from "../components/RegionPicker";
import ScenesList from "../components/ScenesList";
import { useGetRegionsQuery } from "../lib/api";
import { DEFAULT_SCENE_URL } from "../lib/config";
import type { Region } from "../lib/types";

// One stable empty array. Writing `data = []` inline would create a new array on every render,
// and MapView's effect (which depends on `regions`) would then run on every render.
const NO_REGIONS: Region[] = [];

export default function Home() {
  const { data, isError } = useGetRegionsQuery();

  return (
    <div style={{ position: "relative" }}>
      <MapView regions={data ?? NO_REGIONS} sceneUrl={DEFAULT_SCENE_URL} />
      <aside
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          bottom: 0,
          width: 340,
          boxSizing: "border-box",
          padding: 12,
          overflowY: "auto",
          background: "rgba(255, 255, 255, 0.95)",
        }}
      >
        <h1 style={{ margin: "0 0 8px" }}>GeoLens</h1>
        {isError && <p>Could not load the regions. Is the API running?</p>}
        <RegionPicker />
        <FilterForm />
        <ScenesList />
      </aside>
    </div>
  );
}
