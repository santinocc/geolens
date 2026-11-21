import type { NextConfig } from "next";

// The browser only talks to Next.js. Requests to /api/... are forwarded to the real API,
// whose address (API_URL) is read here, on the server, and never sent to the browser.
const API_URL = process.env.API_URL ?? "http://localhost:8001";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/:path*` }];
  },
};

export default nextConfig;
