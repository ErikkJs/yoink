import { DiagramFrame } from "./DiagramFrame";

/**
 * Visualizes the token-bucket rate limiter.
 *
 * - rate: requests per second (default 2.0)
 * - capacity: bucket size / max burst (default 1)
 *
 * Tokens are rendered as filled lime cells inside the bucket. The
 * "refill" badge above the bucket pulses at the configured rate, and
 * the "consume" badge below pulses on each fictional request — the
 * intent is to read like a physical bucket rather than a flow chart.
 */
interface TokenBucketProps {
  rate?: number;
  capacity?: number;
  filled?: number;
}

export function TokenBucket({
  rate = 2.0,
  capacity = 1,
  filled = capacity,
}: TokenBucketProps) {
  // For visual clarity: cap the rendered cell count at 8 to avoid a giant
  // bucket. If user passes capacity=20 we still draw 8 cells with a "+12 more"
  // hint.
  const cellsToDraw = Math.min(capacity, 8);
  const overflow = capacity - cellsToDraw;
  const cells = Array.from({ length: cellsToDraw }, (_, i) => i < filled);

  return (
    <DiagramFrame
      label="rate-limiter / token-bucket"
      source="rate_limiter.py"
      caption={`refill rate: ${rate}/s   ·   capacity: ${capacity}   ·   each fetch consumes one token`}
    >
      <div className="flex flex-col items-center gap-5">
        {/* Refill spout */}
        <div className="flex items-center gap-3">
          <span className="meta-pill text-lime/90">
            <span className="live-dot" />
            refill · {rate}/s
          </span>
        </div>

        {/* Drip arrow */}
        <div className="relative h-10 flex items-center justify-center">
          <div className="w-px h-full bg-gradient-to-b from-transparent via-lime/60 to-lime" />
          <span className="absolute -bottom-0.5 text-lime text-xs">▼</span>
          <span
            className="absolute top-0 size-1.5 rounded-full bg-lime shadow-[0_0_8px_hsl(var(--lime))]"
            style={{ animation: "drop 2s linear infinite" }}
          />
        </div>

        {/* Bucket */}
        <div className="relative">
          {/* Bucket sides */}
          <div
            className="grid gap-1 p-2 rounded-md border-2 border-foreground/30 bg-background relative"
            style={{
              gridTemplateColumns: `repeat(${cellsToDraw}, minmax(0, 1fr))`,
              minWidth: cellsToDraw * 32,
            }}
          >
            {cells.map((isFilled, i) => (
              <span
                key={i}
                className={`h-8 rounded-sm transition-all ${
                  isFilled
                    ? "bg-lime shadow-[inset_0_0_0_1px_hsl(var(--lime-bright)),0_0_8px_-2px_hsl(var(--lime))]"
                    : "bg-muted/40 border border-dashed border-border"
                }`}
                aria-label={isFilled ? "filled token" : "empty slot"}
              />
            ))}
            {/* Side rails for the "bucket" look */}
            <div className="absolute -left-1.5 top-1 bottom-1 w-1.5 bg-foreground/30 rounded-l" />
            <div className="absolute -right-1.5 top-1 bottom-1 w-1.5 bg-foreground/30 rounded-r" />
          </div>

          {/* Bucket label */}
          <div className="mt-2.5 flex items-center justify-center gap-3 text-[0.7rem] font-mono text-muted-foreground">
            <span>
              <span className="text-lime">{filled}</span> /{" "}
              <span className="text-foreground/80">{capacity}</span> tokens
            </span>
            {overflow > 0 && (
              <span className="text-muted-foreground/50">+{overflow} more</span>
            )}
          </div>
        </div>

        {/* Consume arrow */}
        <div className="relative h-10 flex items-center justify-center">
          <div className="w-px h-full bg-gradient-to-b from-cyan/60 via-cyan/60 to-transparent" />
          <span className="absolute -top-0.5 text-cyan text-xs">▲</span>
          <span
            className="absolute bottom-0 size-1.5 rounded-full bg-cyan shadow-[0_0_8px_hsl(var(--cyan))]"
            style={{ animation: "consume 2s linear infinite" }}
          />
        </div>

        {/* Consumer */}
        <div className="flex items-center gap-3">
          <span className="meta-pill text-cyan">
            consume · fetcher.fetch(url)
          </span>
        </div>

        {/* Empty-bucket note */}
        <div className="mt-3 px-3 py-1.5 rounded-md bg-amber/[0.08] border border-amber/30 font-mono text-[0.7rem] text-amber">
          if bucket empty → await (1 - tokens) / rate seconds
        </div>
      </div>

      <style>{`
        @keyframes drop {
          0% { transform: translateY(0); opacity: 0; }
          15% { opacity: 1; }
          85% { opacity: 1; }
          100% { transform: translateY(2.5rem); opacity: 0; }
        }
        @keyframes consume {
          0% { transform: translateY(-2.5rem); opacity: 0; }
          15% { opacity: 1; }
          85% { opacity: 1; }
          100% { transform: translateY(0); opacity: 0; }
        }
        @media (prefers-reduced-motion: reduce) {
          [style*="drop"], [style*="consume"] { animation: none !important; }
        }
      `}</style>
    </DiagramFrame>
  );
}
