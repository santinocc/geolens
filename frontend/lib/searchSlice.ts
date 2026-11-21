import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { Scene } from "./types";

export type Filters = {
  from: string | null; // a date, "2026-11-01"
  to: string | null;
  maxCloud: number | null; // percent
};

export type SearchState = {
  selectedRegionId: string | null;
  filters: Filters;
  selectedScene: Scene | null;
};

export const initialState: SearchState = {
  selectedRegionId: null,
  filters: { from: null, to: null, maxCloud: null },
  selectedScene: null,
};

const searchSlice = createSlice({
  name: "search",
  initialState,
  reducers: {
    selectRegion(state, action: PayloadAction<string | null>) {
      state.selectedRegionId = action.payload;
      state.selectedScene = null;
    },
    setFilters(state, action: PayloadAction<Partial<Filters>>) {
      state.filters = { ...state.filters, ...action.payload};
    },
    clearFilters(state) {
      state.filters = initialState.filters;
    },
    selectScene(state, action: PayloadAction<Scene | null>) {
      state.selectedScene = action.payload;
    },
  },
});

export const { selectRegion, setFilters, clearFilters, selectScene } = searchSlice.actions;
export default searchSlice.reducer;
