"use client";

import { useAppDispatch, useAppSelector } from "../lib/hooks";
import { clearFilters, setFilters } from "../lib/searchSlice";

export default function FilterForm() {
  const filters = useAppSelector((state) => state.search.filters);
  const dispatch = useAppDispatch();

  return (
    <section>
      <h2>Filters</h2>
      <div style={{ display: "grid", gap: 6 }}>
        <label>
          From{" "}
          <input
            type="date"
            value={filters.from ?? ""}
            onChange={(event) => dispatch(setFilters({ from: event.target.value || null }))}
          />
        </label>
        <label>
          To{" "}
          <input
            type="date"
            value={filters.to ?? ""}
            onChange={(event) => dispatch(setFilters({ to: event.target.value || null }))}
          />
        </label>
        <label>
          Max cloud cover (%){" "}
          <input
            type="number"
            min={0}
            max={100}
            step={0.1}
            style={{ width: 70 }}
            value={filters.maxCloud ?? ""}
            onChange={(event) =>
              dispatch(setFilters({ maxCloud: event.target.value === "" ? null : Number(event.target.value) }))
            }
          />
        </label>
        <button onClick={() => dispatch(clearFilters())}>Clear filters</button>
      </div>
    </section>
  );
}
