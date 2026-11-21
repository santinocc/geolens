"use client";

import { useEffect, useState } from "react";

import MapView from "../components/MapView";
import { DEFAULT_SCENE_URL } from "../lib/config";
import type { Region } from "../lib/types";

// Temporary: step 4c replaces this fetch with RTK Query.
export default function Home() {
  const [regions, setRegions] = useState<Region[]>([]);

  useEffect(() => {
    fetch("/api/regions")
      .then((response) => response.json())
      .then(setRegions)
      .catch((error) => console.error("could not load regions", error));
  }, []);

  return <MapView regions={regions} sceneUrl={DEFAULT_SCENE_URL} />;
}
