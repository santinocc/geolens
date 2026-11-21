"use client";

import { useEffect, useState } from "react";

// Temporary page for step 4a: proves the browser can reach the API through the proxy.
export default function Home() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    fetch("/api/health")
      .then((response) => response.json())
      .then((body) => setStatus(body.status))
      .catch(() => setStatus("the API is not reachable"));
  }, []);

  return (
    <main style={{ padding: 24 }}>
      <h1>GeoLens</h1>
      <p>API health: {status}</p>
    </main>
  );
}
