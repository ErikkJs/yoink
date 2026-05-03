import { DiagramFrame } from "./DiagramFrame";

/**
 * The CombinedFilter pipeline: domain → extension → include → exclude → queue.
 * The first filter that says "no" drops the URL.
 */
const stages = [
  {
    name: "domain filter",
    config: "allowed_domains",
    note: "honors subdomains",
    color: "cyan" as const,
    rejects: "wrong domain",
  },
  {
    name: "extension filter",
    config: "skip_extensions",
    note: "fast path-suffix",
    color: "amber" as const,
    rejects: ".pdf, .zip, …",
  },
  {
    name: "include patterns",
    config: "include_patterns",
    note: "must match ≥ 1",
    color: "lime" as const,
    rejects: "no include match",
  },
  {
    name: "exclude patterns",
    config: "exclude_patterns",
    note: "must match 0",
    color: "magenta" as const,
    rejects: "matched exclude",
  },
];

const colorMap = {
  cyan: { border: "border-cyan/40", bg: "bg-cyan/[0.05]", text: "text-cyan" },
  amber: { border: "border-amber/40", bg: "bg-amber/[0.05]", text: "text-amber" },
  lime: { border: "border-lime/40", bg: "bg-lime/[0.05]", text: "text-lime" },
  magenta: { border: "border-magenta/40", bg: "bg-magenta/[0.05]", text: "text-magenta" },
};

export function URLFilterPipeline() {
  return (
    <DiagramFrame
      label="filters / pipeline"
      source="filters.py · CombinedFilter.should_crawl"
      caption="first filter that says 'no' wins. domain runs first because it's the cheapest reject."
    >
      <div className="space-y-3">
        {/* Input */}
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="meta-pill">input</span>
            <code className="font-mono text-sm bg-muted/40 border border-border rounded px-2 py-0.5">
              url
            </code>
          </div>
          <span className="meta-pill text-lime">▸ for every link discovered</span>
        </div>

        {/* Pipeline — horizontal once the diagram has at least 48rem of room. */}
        <div className="grid grid-cols-1 @3xl:grid-cols-[repeat(4,minmax(0,1fr))_auto_1fr_auto] gap-2 @3xl:gap-1.5 items-stretch">
          {stages.map((s, i) => {
            const c = colorMap[s.color];
            return (
              <div key={s.name} className="contents">
                <div
                  className={`relative rounded-lg border ${c.border} ${c.bg} p-3 flex flex-col`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span
                      className={`font-mono text-[0.62rem] uppercase tracking-[0.14em] font-semibold ${c.text}`}
                    >
                      {String(i + 1).padStart(2, "0")} ─ {s.name}
                    </span>
                  </div>
                  <code
                    className={`block font-mono text-[0.78rem] ${c.text} mb-1`}
                  >
                    {s.config}
                  </code>
                  <p className="text-[0.72rem] text-muted-foreground">{s.note}</p>
                </div>
                {/* Arrow between stages — hide on the last */}
                {i < stages.length - 1 && (
                  <div className="hidden @3xl:flex items-center justify-center text-muted-foreground/40 font-mono text-lg">
                    →
                  </div>
                )}
                {i < stages.length - 1 && (
                  <div className="@3xl:hidden flex items-center justify-center text-muted-foreground/40 font-mono py-0.5">
                    ↓
                  </div>
                )}
              </div>
            );
          })}

          {/* Final arrow + queue terminal */}
          <div className="hidden @3xl:flex items-center justify-center text-lime font-mono">
            →
          </div>
          <div className="@3xl:hidden flex items-center justify-center text-lime font-mono py-0.5">
            ↓
          </div>
          <div className="@3xl:col-span-1 col-span-1 flex items-center justify-center rounded-lg border border-lime/50 bg-lime/[0.08] p-3">
            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-lime shadow-[0_0_8px_hsl(var(--lime))]" />
              <span className="font-mono text-sm font-semibold text-lime">queue</span>
            </div>
          </div>
        </div>

        {/* Reject sidebar */}
        <div className="rounded-lg border border-border bg-background/40 px-4 py-3">
          <div className="flex items-baseline gap-2 mb-2">
            <span className="font-mono text-amber text-base leading-none">!</span>
            <p className="meta-pill text-amber">if any stage rejects</p>
          </div>
          <p className="text-[0.82rem] text-muted-foreground">
            URL is dropped and{" "}
            <code className="font-mono text-foreground">filtered</code> set is updated. It
            never reaches the queue, never gets fetched. The stage that rejected is
            logged at <code className="font-mono">debug</code>.
          </p>
        </div>
      </div>
    </DiagramFrame>
  );
}
