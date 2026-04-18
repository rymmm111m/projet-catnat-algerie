"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./theme-toggle";
import {
  Map,
  FileText,
  BarChart3,
  List,
  History,
  Shield,
} from "lucide-react";

const navItems = [
  {
    title: "Cartographie",
    href: "/",
    icon: Map,
    description: "Carte des risques sismiques",
  },
  {
    title: "Classement Wilayas",
    href: "/classement",
    icon: List,
    description: "Ranking par zone RPA",
  },
  {
    title: "Historique Seismes",
    href: "/historique",
    icon: History,
    description: "Seismes passes en Algerie",
  },
  {
    title: "Souscription",
    href: "/souscription",
    icon: FileText,
    description: "Module de souscription",
  },
  {
    title: "Monte Carlo",
    href: "/simulation",
    icon: BarChart3,
    description: "Simulation stochastique",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-72 border-r border-[hsl(var(--border))] bg-[hsl(var(--primary))] dark:bg-[hsl(var(--card))] transition-colors duration-300 hidden lg:block">
      <div className="flex h-full flex-col">
        {/* Logo Section */}
        <div className="flex items-center gap-3 border-b border-white/10 dark:border-[hsl(var(--border))] px-6 py-5">
          <div className="relative h-12 w-12 overflow-hidden rounded-xl bg-white/10 p-1.5">
            <Image
              src="/logo.png"
              alt="CATNAT Logo"
              width={48}
              height={48}
              className="object-contain"
            />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white dark:text-[hsl(var(--foreground))]">
              CATNAT
            </h1>
            <p className="text-xs text-white/70 dark:text-[hsl(var(--muted-foreground))]">
              Systeme Expert Sismique
            </p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-white/50 dark:text-[hsl(var(--muted-foreground))]">
            Modules
          </p>
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-white/20 dark:bg-[hsl(var(--accent))] text-white dark:text-[hsl(var(--accent-foreground))] shadow-lg"
                    : "text-white/80 dark:text-[hsl(var(--muted-foreground))] hover:bg-white/10 dark:hover:bg-[hsl(var(--muted))] hover:text-white dark:hover:text-[hsl(var(--foreground))]"
                )}
              >
                <item.icon
                  className={cn(
                    "h-5 w-5 transition-transform duration-200 group-hover:scale-110",
                    isActive && "text-[hsl(var(--accent))] dark:text-[hsl(var(--accent-foreground))]"
                  )}
                />
                <div className="flex-1">
                  <span className="block">{item.title}</span>
                  <span className="block text-xs text-white/50 dark:text-[hsl(var(--muted-foreground))] font-normal">
                    {item.description}
                  </span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-white/10 dark:border-[hsl(var(--border))] p-4">
          <div className="flex items-center justify-between rounded-xl bg-white/10 dark:bg-[hsl(var(--muted))] px-4 py-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-[hsl(var(--accent))]" />
              <span className="text-xs text-white/70 dark:text-[hsl(var(--muted-foreground))]">
                Mode
              </span>
            </div>
            <ThemeToggle />
          </div>
          <p className="mt-4 px-2 text-center text-[10px] text-white/40 dark:text-[hsl(var(--muted-foreground))]">
            Evaluation du risque sismique CATNAT
          </p>
        </div>
      </div>
    </aside>
  );
}
