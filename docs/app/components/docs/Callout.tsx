import * as React from "react";
import { cn } from "../../lib/utils";

type CalloutVariant = "info" | "tip" | "warning" | "danger" | "note";

interface CalloutProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CalloutVariant;
  title?: string;
}

const variantConfig: Record<
  CalloutVariant,
  { border: string; text: string; label: string; glyph: string }
> = {
  info: {
    border: "border-cyan/30 bg-cyan/[0.04]",
    text: "text-cyan",
    label: "Note",
    glyph: "i",
  },
  tip: {
    border: "border-lime/30 bg-lime/[0.04]",
    text: "text-lime",
    label: "Tip",
    glyph: "★",
  },
  warning: {
    border: "border-amber/30 bg-amber/[0.04]",
    text: "text-amber",
    label: "Warning",
    glyph: "!",
  },
  danger: {
    border: "border-destructive/30 bg-destructive/[0.04]",
    text: "text-destructive",
    label: "Danger",
    glyph: "×",
  },
  note: {
    border: "border-magenta/30 bg-magenta/[0.04]",
    text: "text-magenta",
    label: "Detail",
    glyph: "§",
  },
};

export function Callout({
  variant = "info",
  title,
  children,
  className,
  ...props
}: CalloutProps) {
  const cfg = variantConfig[variant];
  return (
    <aside
      className={cn(
        "my-6 rounded-lg border px-5 py-4 flex gap-4 relative",
        cfg.border,
        className
      )}
      {...props}
    >
      <div
        className={cn(
          "shrink-0 size-6 rounded-full grid place-items-center font-mono text-sm font-bold border",
          cfg.text,
          cfg.border
        )}
        aria-hidden="true"
      >
        {cfg.glyph}
      </div>
      <div className="flex-1 min-w-0 space-y-1.5 pt-0.5">
        <p className={cn("font-mono text-[0.7rem] uppercase tracking-[0.14em] font-medium", cfg.text)}>
          {title || cfg.label}
        </p>
        <div className="text-[0.92rem] text-foreground/85 leading-[1.65] [&>p]:my-1.5 [&>p:last-child]:mb-0 [&>p:first-child]:mt-0">
          {children}
        </div>
      </div>
    </aside>
  );
}
