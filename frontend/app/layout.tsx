import type { ReactNode } from "react";

export const metadata = {
  title: "GeoLens",
  description: "Explore Sentinel-2 satellite imagery of Chiba and Tokyo Bay",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif" }}>{children}</body>
    </html>
  );
}
