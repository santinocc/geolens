import { describe, expect, it } from "vitest";

import reducer, { clearFilters, initialState, selectRegion, selectScene, setFilters } from "./searchSlice";
import type { Scene } from "./types";

const scene: Scene = {
  id: "s1",
  acquired_at: "2026-01-01T00:00:00Z",
  cloud_cover: 1,
  cog_url: "https://example.com/s1.tif",
  metres_away: null,
  covered_pct: 100,
};

describe("searchSlice", () => {
  it("selectScene stores the scene", () => {
    const state = reducer(initialState, selectScene(scene));
    expect(state.selectedScene).toEqual(scene);
  });
    it("setFilters changes only the filters it is given", () => {
    const before = { ...initialState, filters: { from: null, to: null, maxCloud: 10}};
    const after = reducer(before, setFilters({ from: "2026-01-01"}));
    expect(after.filters).toEqual({ from: "2026-01-01", to: null, maxCloud: 10});
  });
    it("clearFilters resets every filter", () => {
    const before = { ...initialState, filters: {from: null, to: "2026-02-01", maxCloud: 10}}
    const after = reducer(before, clearFilters());
    expect(after.filters).toEqual(initialState.filters);
  });
    it("selectRegion stores the region and forgets the selected scene", () => {
    const before = { ...initialState, selectedRegionId: "a", selectedScene: scene }
    const after = reducer(before, selectRegion("b"));
    expect(after.selectedRegionId).toEqual("b");
    expect(after.selectedScene).toBeNull();
  });
    it("selectRegion keeps the filters", () => {
    const before = { ...initialState, filters: { from: null, to: null, maxCloud: 10}}
    const after = reducer(before, selectRegion("b"));
    expect(after.filters.maxCloud).toEqual(10);
  });
});