import { DiagramFrame } from "./DiagramFrame";

/**
 * The robots.txt decision flow. Every URL passes through this gate
 * before being queued. Outcome is binary: queue or skip.
 */
export function RobotsFlow() {
  return (
    <DiagramFrame
      label="robots / decision flow"
      source="robots.py"
      caption="evaluated before every URL is added to the queue. 1-hour cache per domain."
    >
      <div className="flex flex-col items-stretch gap-3">
        {/* Input */}
        <div className="self-start flex items-center gap-2">
          <span className="meta-pill">input</span>
          <code className="font-mono text-sm text-foreground bg-muted/40 border border-border rounded px-2 py-0.5">
            url
          </code>
          <span className="text-muted-foreground/50">→</span>
        </div>

        {/* The checker box */}
        <div className="rounded-lg border border-cyan/40 bg-cyan/[0.04] p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="meta-pill text-cyan">RobotsChecker</span>
            <span className="font-mono text-[0.65rem] text-cyan/70">async</span>
          </div>
          <ol className="space-y-1.5">
            {[
              { num: "01", label: "cached for this domain?", aside: "TTL: 1h" },
              { num: "02", label: "if not, fetch /robots.txt", aside: "uses Crawler's Fetcher" },
              { num: "03", label: "match user_agent block", aside: "exact → partial → *" },
              { num: "04", label: "apply Allow / Disallow rules", aside: "longest path wins" },
            ].map((s) => (
              <li key={s.num} className="flex items-baseline gap-3 text-[0.85rem]">
                <span className="font-mono text-[0.7rem] text-cyan/80 tabular-nums shrink-0 w-5">
                  {s.num}
                </span>
                <span className="text-foreground flex-1">{s.label}</span>
                <span className="font-mono text-[0.65rem] text-muted-foreground hidden @md:inline">
                  {s.aside}
                </span>
              </li>
            ))}
          </ol>
        </div>

        {/* Branch */}
        <div className="flex items-center justify-center my-1">
          <span className="meta-pill text-muted-foreground">▼ outcome</span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {/* Allowed branch */}
          <div className="rounded-lg border border-lime/40 bg-lime/[0.04] p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="size-2 rounded-full bg-lime shadow-[0_0_8px_hsl(var(--lime))]" />
              <span className="font-mono text-xs uppercase tracking-wider text-lime font-medium">
                allowed
              </span>
            </div>
            <code className="block font-mono text-[0.8rem] text-foreground/90">
              fetcher.fetch(url)
            </code>
            <p className="mt-1 text-[0.75rem] text-muted-foreground">
              continues to rate-limit gate
            </p>
          </div>

          {/* Blocked branch */}
          <div className="rounded-lg border border-amber/30 bg-amber/[0.04] p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="size-2 rounded-full bg-amber" />
              <span className="font-mono text-xs uppercase tracking-wider text-amber font-medium">
                blocked
              </span>
            </div>
            <code className="block font-mono text-[0.8rem] text-foreground/90">
              skip + log + return
            </code>
            <p className="mt-1 text-[0.75rem] text-muted-foreground">
              never enters the queue
            </p>
          </div>
        </div>
      </div>
    </DiagramFrame>
  );
}
