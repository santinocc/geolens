"use client";

import { useAppSelector } from "../lib/hooks";

// Sampled from Titiler's "rdylgn" colour map (red, yellow, green), the one the NDVI tiles use.
const GRADIENT =
  "linear-gradient(to right, rgb(165,0,38), rgb(222,63,46), rgb(248,142,82), rgb(253,212,129), " +
  "rgb(254,254,189), rgb(203,232,129), rgb(132,202,102), rgb(42,159,84), rgb(0,104,55))";

export default function NdviLegend() {
  const view = useAppSelector((state) => state.search.view);
  const hasScene = useAppSelector((state) => state.search.selectedScene !== null);

  if (view !== "ndvi" || !hasScene) return null;

  return (
    <section>
      <h2>NDVI</h2>
      <div style={{ height: 14, background: GRADIENT, border: "1px solid #888" }} />
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
        <span>-1</span>
        <span>0</span>
        <span>1</span>
      </div>
      <p style={{ margin: "4px 0", fontSize: 13 }}>
        Water and clouds are low, bare ground and cities are near 0, dense plants are high. Computed per tile from the
        red and near-infrared bands.
      </p>
    </section>
  );
}
