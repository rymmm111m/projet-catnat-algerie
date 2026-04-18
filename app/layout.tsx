import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Sidebar } from "@/components/sidebar";
import { LeafletCSS } from "@/components/leaflet-css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CATNAT Algerie - Systeme Expert Sismique",
  description: "Systeme d'evaluation de l'exposition au risque sismique en Algerie",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#1B5E20" },
    { media: "(prefers-color-scheme: dark)", color: "#0f1a10" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" suppressHydrationWarning className="h-full">
      <body className={`${inter.className} min-h-full bg-[hsl(var(--background))]`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange={false}
        >
          <LeafletCSS />
          <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 lg:ml-72 p-4 lg:p-8 overflow-auto">
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
