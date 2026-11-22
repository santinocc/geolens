import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { Scene } from "./types";

export type Filters = {
  from: string | null; // a date, "2026-11-01"
  to: string | null;
  maxCloud: number | null; // percent
};

// A union type: a value of this type can only be one of these two strings.
export type View = "true-colour" | "ndvi";

export type SearchState = {
  selectedRegionId: string | null;
  filters: Filters;
  selectedScene: Scene | null;
  view: View;
};

export const initialState: SearchState = {
  selectedRegionId: null,
  filters: { from: null, to: null, maxCloud: null },
  selectedScene: null,
  view: "true-colour",
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
    setView(state, action: PayloadAction<View>) {
      state.view = action.payload;
    },
  },
});

export const { selectRegion, setFilters, clearFilters, selectScene, setView } = searchSlice.actions;
export default searchSlice.reducer;
