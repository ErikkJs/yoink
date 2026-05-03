import { DiagramFrame } from "./DiagramFrame";

/**
 * Visualizes the JSONL checkpoint file as a stack of typed records.
 * Each record is shown with its `type` discriminator highlighted and
 * a brief explanation of when it gets written.
 */

const records = [
  {
    type: "metadata",
    color: "amber" as const,
    when: "once at start",
    json: `{"type":"metadata","start_url":"https://example.com","config":{...},"started_at":"2026-05-03T12:00:00"}`,
  },
  {
    type: "page",
    color: "lime" as const,
    when: "streamed as crawled",
    json: `{"type":"page","url":"https://example.com","title":"Example","text":"…","depth":0}`,
  },
  {
    type: "page",
    color: "lime" as const,
    when: "…",
    json: `{"type":"page","url":"https://example.com/about","title":"About","text":"…","depth":1}`,
  },
  {
    type: "state",
    color: "cyan" as const,
    when: "every flush_interval pages + on shutdown",
    json: `{"type":"state","visited":[…87 urls…],"queue":[…12 urls…],"filtered":[…5 urls…]}`,
  },
];

const colorMap = {
  amber: "border-amber/40 text-amber bg-amber/[0.05]",
  lime: "border-lime/40 text-lime bg-lime/[0.04]",
  cyan: "border-cyan/40 text-cyan bg-cyan/[0.04]",
};

export function CheckpointRecords() {
  return (
    <DiagramFrame
      label="checkpoint / file format"
      source="crawl.jsonl"
      caption="three record types share one file. resume reads the whole file once and reconstitutes state."
    >
      <div className="space-y-1.5">
        {records.map((r, i) => (
          <div
            key={i}
            className="grid grid-cols-[auto_auto_minmax(0,1fr)] items-start gap-3 group"
          >
            {/* Line number */}
            <span className="font-mono text-[0.65rem] text-muted-foreground/50 tabular-nums pt-2 select-none">
              {String(i + 1).padStart(3, "0")}
            </span>

            {/* Type chip */}
            <span
              className={`font-mono text-[0.65rem] uppercase tracking-[0.1em] font-semibold rounded px-1.5 py-0.5 border shrink-0 mt-1.5 ${colorMap[r.color]}`}
            >
              {r.type}
            </span>

            {/* JSON content */}
            <div className="min-w-0 rounded-md border border-border bg-[hsl(var(--code-bg))] px-3 py-1.5 group-hover:border-border-strong transition-colors">
              <code className="font-mono text-[0.78rem] text-foreground/85 whitespace-nowrap overflow-x-auto block">
                {r.json}
              </code>
              <p className="mt-1 font-mono text-[0.65rem] text-muted-foreground/70">
                ↳ {r.when}
              </p>
            </div>
          </div>
        ))}

        {/* Pagination ellipsis */}
        <div className="grid grid-cols-[auto_auto_minmax(0,1fr)] items-center gap-3 pt-2">
          <span className="font-mono text-[0.65rem] text-muted-foreground/30 select-none">···</span>
          <span className="font-mono text-[0.65rem] text-muted-foreground/40">…</span>
          <span className="font-mono text-[0.7rem] text-muted-foreground/60 italic">
            file grows append-only as the crawl progresses
          </span>
        </div>
      </div>
    </DiagramFrame>
  );
}
