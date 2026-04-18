"use client";

import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="h-8 w-14 rounded-full bg-white/20 dark:bg-[hsl(var(--muted))]" />
    );
  }

  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="relative h-8 w-14 rounded-full bg-white/20 dark:bg-[hsl(var(--primary))] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent))] focus:ring-offset-2"
      aria-label="Toggle theme"
    >
      <div
        className={`absolute top-1 h-6 w-6 rounded-full bg-white dark:bg-[hsl(var(--accent))] shadow-md transition-transform duration-300 flex items-center justify-center ${
          theme === "dark" ? "translate-x-7" : "translate-x-1"
        }`}
      >
        {theme === "dark" ? (
          <Moon className="h-3.5 w-3.5 text-[hsl(var(--primary))]" />
        ) : (
          <Sun className="h-3.5 w-3.5 text-[hsl(var(--primary))]" />
        )}
      </div>
    </button>
  );
}
