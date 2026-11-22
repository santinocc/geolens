import { describe, expect, it } from "vitest";

import { ndviTileUrl, tileUrl, mapTilesUrl } from "./titiler";
import type { Scene } from "./types";
import type { View } from "./searchSlice";
import { DEFAULT_SCENE_URL } from "./config";

const scene: Scene = {
  id: "s1",
  acquired_at: "2026-01-01T00:00:00Z",
  cloud_cover: 1,
  cog_url: "https://example.com/s1.tif",
  metres_away: null,
  covered_pct: 100,
};

describe("ndviTileUrl", () => {
  it("reads both the red and the near-infrared band, in that order", () => {
    const url = ndviTileUrl("S2C_54SVE_20261028_0_L2A");
    expect(url).toContain("assets=red&assets=nir");
  });
  it("the formula is encoded", () => {
    const url = ndviTileUrl("S2C_54SVE_20261028_0_L2A");
    const formula = encodeURIComponent("(b2-b1)/(b2+b1)");
    expect(url).toContain(`expression=${formula}`);
    expect(url).not.toContain("b2+b1");
  });
    it("the catalog URL carries the id", () => {
    const id = "S2C_54SVE_20261028_0_L2A";
    const CATALOG = "https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/";
    const expected = encodeURIComponent(CATALOG + id);
    const url = ndviTileUrl(id);
    expect(url).toContain(`url=${expected}`);
  });
});

describe("mapTilesUrl", () => {
  it("no scene -> the default image", () => {
    const url1 = mapTilesUrl(null, "true-colour");
    const url2 = mapTilesUrl(null, "ndvi");
    expect(url1).toEqual(tileUrl(DEFAULT_SCENE_URL));
    expect(url2).toEqual(tileUrl(DEFAULT_SCENE_URL));
  });
  it("a scene and true colour -> that scene's image", () => {
    const url = mapTilesUrl(scene, "true-colour");
    expect(url).toEqual(tileUrl(scene.cog_url));
  });
    it("a scene and NDVI -> that scene's NDVI", () => {
    const url = mapTilesUrl(scene, "ndvi");
    expect(url).toEqual(ndviTileUrl(scene.id));
  });
});