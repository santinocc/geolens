"use client";

import { skipToken } from "@reduxjs/toolkit/query";

import { useGetRegionScenesQuery } from "../lib/api";
import { useAppDispatch, useAppSelector } from "../lib/hooks";
import { selectScene } from "../lib/searchSlice";

export default function ScenesList() {
  const regionId = useAppSelector((state) => state.search.selectedRegionId);
  const filters = useAppSelector((state) => state.search.filters);
  const selectedScene = useAppSelector((state) => state.search.selectedScene);
  const dispatch = useAppDispatch();

  // skipToken means "do not fetch yet": there is nothing to ask until a region is picked.
  // The store keeps null for "no value", and the query's arguments use undefined for "leave it out".
  const { data: scenes, isFetching, isError } = useGetRegionScenesQuery(
    regionId
      ? {
          regionId,
          from: filters.from ?? undefined,
          to: filters.to ?? undefined,
          maxCloud: filters.maxCloud ?? undefined,
          limit: 20,
        }
      : skipToken,
  );

  if (!regionId) return <p>Pick a region to see its scenes.</p>;
  if (isError) return <p>Could not load the scenes. Is the API running?</p>;

  return (
    <section style={{ opacity: isFetching ? 0.5 : 1 }}>
      <h2>Scenes{scenes ? ` (${scenes.length})` : ""}</h2>
      {scenes?.length === 0 && <p>No scenes match these filters.</p>}
      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 6 }}>
        {scenes?.map((scene) => (
          <li key={scene.id}>
            <button
              data-testid="scene"
              aria-pressed={scene.id === selectedScene?.id}
              onClick={() => dispatch(selectScene(scene))}
              style={{ width: "100%", textAlign: "left", fontWeight: scene.id === selectedScene?.id ? 700 : 400 }}
            >
              {scene.acquired_at.slice(0, 10)} · cloud {scene.cloud_cover.toFixed(1)}% · covers{" "}
              {scene.covered_pct?.toFixed(0) ?? "?"}% of the region
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
