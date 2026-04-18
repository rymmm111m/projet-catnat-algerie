import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  variant?: "default" | "primary" | "warning" | "danger" | "success";
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendValue,
  variant = "default",
}: MetricCardProps) {
  const variantStyles = {
    default: "bg-[hsl(var(--card))] border-[hsl(var(--border))]",
    primary: "bg-[hsl(var(--primary))]/10 border-[hsl(var(--primary))]/20",
    warning: "bg-orange-500/10 border-orange-500/20",
    danger: "bg-red-500/10 border-red-500/20",
    success: "bg-green-500/10 border-green-500/20",
  };

  const iconStyles = {
    default: "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]",
    primary: "bg-[hsl(var(--primary))]/20 text-[hsl(var(--primary))]",
    warning: "bg-orange-500/20 text-orange-600 dark:text-orange-400",
    danger: "bg-red-500/20 text-red-600 dark:text-red-400",
    success: "bg-green-500/20 text-green-600 dark:text-green-400",
  };

  return (
    <div
      className={cn(
        "rounded-2xl border p-5 transition-all duration-200 hover:shadow-md",
        variantStyles[variant]
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-[hsl(var(--muted-foreground))]">
            {title}
          </p>
          <p className="mt-2 text-2xl font-bold text-[hsl(var(--foreground))]">
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
              {subtitle}
            </p>
          )}
          {trend && trendValue && (
            <div
              className={cn(
                "mt-2 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
                trend === "up" && "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
                trend === "down" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                trend === "neutral" && "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
              )}
            >
              {trend === "up" && "↑"}
              {trend === "down" && "↓"}
              {trendValue}
            </div>
          )}
        </div>
        {Icon && (
          <div className={cn("rounded-xl p-3", iconStyles[variant])}>
            <Icon className="h-5 w-5" />
          </div>
        )}
      </div>
    </div>
  );
}
