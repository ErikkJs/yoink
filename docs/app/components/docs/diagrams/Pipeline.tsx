import * as React from "react";
import { cn } from "../../../lib/utils";

type Accent = "lime" | "cyan" | "amber" | "magenta" | "neutral";

export interface PipelineStep {
  label: string;
  /** Optional secondary line — e.g. tooling, hint, output type. */
  hint?: string;
  /** Per-step accent override. Defaults to the parent's accent. */
  accent?: Accent;
}

interface PipelineProps {
  steps: (string | PipelineStep)[];
  /** Default accent — the final step always uses lime to mark "output". */
  accent?: Accent;
  /** Show 01 / 02 / … numerals on each step. Defaults to true. */
  numbered?: boolean;
  className?: string;
}

const accentMap: Record<Accent, { border: string; text: string; bg: string }> = {
  lime: {
    border: "border-lime/40",
    text: "text-lime",
    bg: "bg-lime/[0.05]",
  },
  cyan: {
    border: "border-cyan/40",
    text: "text-cyan",
    bg: "bg-cyan/[0.05]",
  },
  amber: {
    border: "border-amber/40",
    text: "text-amber",
    bg: "bg-amber/[0.05]",
  },
  magenta: {
    border: "border-magenta/40",
    text: "text-magenta",
    bg: "bg-magenta/[0.05]",
  },
  neutral: {
    border: "border-border-strong",
    text: "text-foreground",
    bg: "bg-card/40",
  },
};

/**
 * A compact horizontal pipeline visualization.
 *
 * Designed for short 3–7 step flows that read as a sentence — lighter
 * chrome than `DiagramFrame`, suitable for inline use inside a section.
 *
 *     <Pipeline steps={["crawl", "filter", "dedupe", "JSONL"]} />
 *
 *     <Pipeline
 *       steps={[
 *         { label: "crawl", hint: "Crawler" },
 *         { label: "filter", hint: "len ≥ 500" },
 *         { label: "JSONL", hint: "one record/page", accent: "lime" },
 *       ]}
 *     />
 */
export function Pipeline({
  steps,
  accent = "neutral",
  numbered = true,
  className,
}: PipelineProps) {
  // Normalize steps + force lime on the final step (output marker)
  const normalized: PipelineStep[] = steps.map((s, i) => {
    const base = typeof s === "string" ? { label: s } : s;
    const isLast = i === steps.length - 1;
    return {
      ...base,
      accent: base.accent ?? (isLast ? "lime" : accent),
    };
  });

  return (
    <div
      className={cn(
        "@container my-6 rounded-xl border border-border-strong bg-card/30 px-5 py-5 overflow-x-auto",
        className
      )}
    >
      <ol
        className={cn(
          "flex items-stretch gap-0 min-w-min",
          "flex-wrap @2xl:flex-nowrap"
        )}
      >
        {normalized.map((step, i) => {
          const c = accentMap[step.accent ?? "neutral"];
          const isLast = i === normalized.length - 1;
          return (
            <React.Fragment key={`${step.label}-${i}`}>
              <li
                className={cn(
                  "flex flex-col rounded-lg border px-3.5 py-2.5 min-w-[7rem] flex-1",
                  c.border,
                  c.bg
                )}
              >
                <div className="flex items-baseline gap-2">
                  {numbered && (
                    <span
                      className={cn(
                        "font-mono text-[0.62rem] uppercase tracking-[0.14em] tabular-nums shrink-0",
                        c.text
                      )}
                    >
                      {String(i + 1).padStart(2, "0")}
                    </span>
                  )}
                  <span className="font-display text-[0.95rem] font-semibold text-foreground leading-tight">
                    {step.label}
                  </span>
                </div>
                {step.hint && (
                  <span className="font-mono text-[0.68rem] text-muted-foreground mt-1 leading-tight">
                    {step.hint}
                  </span>
                )}
              </li>

              {!isLast && (
                <div
                  className="hidden @2xl:flex items-center justify-center px-2 text-muted-foreground/40 select-none"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 16 16" className="size-3.5" fill="currentColor">
                    <path d="M5 2l6 6-6 6V2z" />
                  </svg>
                </div>
              )}
              {!isLast && (
                <div
                  className="@2xl:hidden flex items-center justify-center w-full text-muted-foreground/40 select-none py-1"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 16 16" className="size-3.5 rotate-90" fill="currentColor">
                    <path d="M5 2l6 6-6 6V2z" />
                  </svg>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </ol>
    </div>
  );
}
