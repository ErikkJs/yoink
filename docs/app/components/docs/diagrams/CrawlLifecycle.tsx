import { DiagramFrame } from "./DiagramFrame";

/**
 * The Crawler worker loop, rendered as a numbered vertical pipeline.
 * Each step is a real method on a real module; tags on the right
 * call out which module owns that step.
 */
const steps = [
  {
    label: "Scheduler.add(start_url, depth=0)",
    detail: "seed the queue with the start URL",
    owner: "scheduler.py",
    color: "lime" as const,
    pre: true,
  },
  {
    label: "spawn N workers",
    detail: "max_concurrency coroutines, each running the inner loop",
    owner: "crawler.py",
    color: "lime" as const,
    pre: true,
  },
  {
    label: "RateLimiter.acquire(domain)",
    detail: "wait for a token in the per-domain bucket",
    owner: "rate_limiter.py",
    color: "amber" as const,
  },
  {
    label: "RobotsChecker.is_allowed(url)",
    detail: "fetch & cache robots.txt, evaluate rules",
    owner: "robots.py",
    color: "amber" as const,
  },
  {
    label: "Fetcher.fetch(url) → html, status",
    detail: "aiohttp or Playwright, depending on render_js",
    owner: "fetcher.py",
    color: "cyan" as const,
  },
  {
    label: "Parser.parse(html) → title, links, metadata",
    detail: "BeautifulSoup + lxml",
    owner: "parser.py",
    color: "magenta" as const,
  },
  {
    label: "Extractor.extract(html) → text",
    detail: "trafilatura, optional",
    owner: "extractor.py",
    color: "magenta" as const,
  },
  {
    label: "CheckpointManager.write_page(page)",
    detail: "JSONL append to disk or S3",
    owner: "checkpoint.py",
    color: "lime" as const,
  },
  {
    label: "Scheduler.add(link, depth+1) for link in links",
    detail: "enqueue children, dedup against visited",
    owner: "scheduler.py",
    color: "lime" as const,
  },
];

const colorMap = {
  lime: { border: "border-lime/40", text: "text-lime", bg: "bg-lime/[0.04]" },
  amber: { border: "border-amber/40", text: "text-amber", bg: "bg-amber/[0.04]" },
  cyan: { border: "border-cyan/40", text: "text-cyan", bg: "bg-cyan/[0.04]" },
  magenta: { border: "border-magenta/40", text: "text-magenta", bg: "bg-magenta/[0.04]" },
};

export function CrawlLifecycle() {
  return (
    <DiagramFrame
      label="crawler / worker loop"
      source="crawler.py"
      caption="async workers run the same inner loop. exit when queue empty AND no in-flight work."
    >
      <div className="space-y-6">
        {/* Setup steps (run once) */}
        <div className="space-y-1.5">
          <p className="meta-pill mb-2">▸ setup (run once)</p>
          {steps.filter((s) => s.pre).map((s, i) => (
            <Step key={s.label} step={s} index={i} />
          ))}
        </div>

        {/* Visual divider */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-gradient-to-r from-border via-border-strong to-border" />
          <span className="meta-pill text-lime">▸ inner loop · per URL · per worker</span>
          <div className="flex-1 h-px bg-gradient-to-r from-border via-border-strong to-border" />
        </div>

        {/* Loop steps */}
        <div className="space-y-1.5">
          {steps.filter((s) => !s.pre).map((s, i) => (
            <Step key={s.label} step={s} index={i} />
          ))}
          <div className="ml-7 mt-3 flex items-center gap-2 text-[0.75rem] text-muted-foreground">
            <span className="font-mono text-lime">↻</span>
            <span className="italic">repeat until queue is empty</span>
          </div>
        </div>
      </div>
    </DiagramFrame>
  );
}

function Step({ step, index }: { step: (typeof steps)[number]; index: number }) {
  const c = colorMap[step.color];
  return (
    <div
      className={`flex items-start gap-3 rounded-md pl-3 pr-3 py-2 border-l-2 ${c.border} ${c.bg}`}
    >
      <span className="font-mono text-[0.65rem] text-muted-foreground/70 shrink-0 w-5 mt-0.5 tabular-nums">
        {String(index + 1).padStart(2, "0")}
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-mono text-[0.85rem] text-foreground leading-snug">
          {step.label}
        </p>
        <p className="text-[0.78rem] text-muted-foreground mt-0.5">{step.detail}</p>
      </div>
      <span
        className={`font-mono text-[0.65rem] ${c.text} shrink-0 mt-0.5 hidden @md:inline`}
      >
        {step.owner}
      </span>
    </div>
  );
}
