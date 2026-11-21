"use client";

import { useGetRegionsQuery } from "../lib/api";
import { useAppDispatch, useAppSelector } from "../lib/hooks";
import { selectRegion } from "../lib/searchSlice";

export default function RegionPicker() {
  const { data: regions } = useGetRegionsQuery();
  const selectedId = useAppSelector((state) => state.search.selectedRegionId);
  const dispatch = useAppDispatch();

  return (
    <section>
      <h2>Region</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {regions?.map((region) => (
          <button
            key={region.id}
            aria-pressed={region.id === selectedId}
            onClick={() => dispatch(selectRegion(region.id))}
            style={{ fontWeight: region.id === selectedId ? 700 : 400 }}
          >
            {region.name}
          </button>
        ))}
      </div>
    </section>
  );
}
