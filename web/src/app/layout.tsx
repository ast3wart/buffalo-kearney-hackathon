import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { Nav } from "@/components/Nav";


export const metadata: Metadata = {
  title: "Equipment X-Ray",
  description: "Pre-deal equipment diligence: CapEx cliff, single points of failure, and parts sourcing.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <Suspense>
          <Nav />
        </Suspense>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
