// NEXT_PUBLIC_ variables are sent to the browser, so they must never hold secrets.
// Titiler is called by the browser directly (map tiles are not worth proxying through Node).
export const TITILER_URL = process.env.NEXT_PUBLIC_TITILER_URL ?? "http://localhost:8000";

// The Sentinel-2 scene of Stage 1. Step 4e replaces this with the scene the user picks.
export const DEFAULT_SCENE_URL =
  "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/54/S/VE/2026/1/S2B_54SVE_20260116_0_L2A/TCI.tif";
