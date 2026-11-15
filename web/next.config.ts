import type { NextConfig } from "next";

// STATIC_EXPORT=1 builds a static snapshot for GitHub Pages (scripts/deploy_pages.sh); otherwise a normal app.
const isStatic = process.env.STATIC_EXPORT === "1";
const base = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = isStatic
  ? { output: "export", basePath: base, trailingSlash: true, images: { unoptimized: true } }
  : {};

export default nextConfig;
