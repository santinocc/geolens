import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import type { Region, Scene } from "./types";

type RegionScenesArgs = {
  regionId: string;
  from?: string;
  to?: string;
  maxCloud?: number;
  limit?: number;
};

// RTK Query: every endpoint becomes a cached query with loading and error state.
// The browser calls /api/..., and Next.js forwards it to the real API (see next.config.ts).
export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  endpoints: (builder) => ({
    getRegions: builder.query<Region[], void>({
      query: () => "/regions",
    }),
    getRegionScenes: builder.query<Scene[], RegionScenesArgs>({
      query: ({ regionId, from, to, maxCloud, limit }) => ({
        url: `/regions/${regionId}/scenes`,
        params: { from, to, max_cloud: maxCloud, limit },
  }),
}),
  }),
});

export const { useGetRegionsQuery, useGetRegionScenesQuery } = api;
