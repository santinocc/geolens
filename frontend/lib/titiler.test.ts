import { describe, expect, it } from "vitest";

import { ndviTileUrl } from "./titiler";


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