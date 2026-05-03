import * as React from "react";
import { cn } from "../../../lib/utils";

interface DiagramFrameProps {
  label?: string;
  caption?: string;
  source?: string;
  className?: string;
  children: React.ReactNode;
}

/**
 * Wraps every concept diagram in a consistent bordered frame with
 * monospace metadata labels — gives the diagrams a distinct visual
 * voice from regular code blocks.
 */
export function DiagramFrame({
  label,
  caption,
  source,
  className,
  children,
}: DiagramFrameProps) {
  return (
    <figure
      className={cn(
        "my-8 rounded-xl border border-border-strong bg-card/30 overflow-hidden",
        className
      )}
    >
      {(label || source) && (
        <header className="flex items-center justify-between gap-3 px-4 py-2 border-b border-border bg-background/40">
          {label && <span className="meta-pill">{label}</span>}
          {source && (
            <span className="font-mono text-[0.65rem] text-muted-foreground/70">
              {source}
            </span>
          )}
        </header>
      )}
      {/* @container makes every diagram respond to ITS OWN width, not the
          viewport's. Children opt into responsive layouts via @md, @lg, @xl
          (~28rem / 32rem / 36rem container width). */}
      <div className="@container p-5 @md:p-6 @lg:p-8">{children}</div>
      {caption && (
        <figcaption className="px-4 py-2.5 border-t border-border bg-background/40 font-mono text-[0.7rem] text-muted-foreground">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}
