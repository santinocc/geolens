import type { ReactNode } from "react";

import StoreProvider from "../components/StoreProvider";

export const metadata = {
  title: "GeoLens",
  description: "Explore Sentinel-2 satellite imagery of Chiba and Tokyo Bay",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif" }}>
        <StoreProvider>{children}</StoreProvider>
      </body>
    </html>
  );
}
