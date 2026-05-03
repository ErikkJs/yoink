import { Link } from "react-router";
import type { Route } from "./+types/_index";
import { TopBar } from "../components/layout/TopBar";
import { Button } from "../components/ui/button";

export function meta(_: Route.MetaArgs) {
  return [
    { title: "yoink — the public data crawler" },
    {
      name: "description",
      content:
        "Fast, async Python web crawler for extracting clean, AI-ready data from public websites. Rate-limited, robots-aware, and resumable.",
    },
  ];
}

const features = [
  {
    n: "01",
    title: "async by default",
    body: "aiohttp-based concurrency with configurable workers. Hundreds of pages per minute on a single laptop, polite by default.",
    tags: ["aiohttp", "asyncio"],
    accent: "lime" as const,
  },
  {
    n: "02",
    title: "AI-ready text",
    body: "Trafilatura-powered extraction returns clean prose with the chrome stripped. Pipe straight into your training set.",
    tags: ["trafilatura", "lxml"],
    accent: "cyan" as const,
  },
  {
    n: "03",
    title: "token-bucket rate limiter",
    body: "Per-domain limits with crawl-delay honoring. Be a good citizen without thinking about it.",
    tags: ["robots.txt", "per-domain"],
    accent: "amber" as const,
  },
  {
    n: "04",
    title: "resumable crawls",
    body: "Append-only checkpoints to disk or S3. Survives Lambda timeouts, OOM kills, and Ctrl-C — pick right back up.",
    tags: ["aioboto3", "JSONL"],
    accent: "magenta" as const,
  },
  {
    n: "05",
    title: "JS rendering, optional",
    body: "Drop-in Playwright for SPAs. Chromium / Firefox / WebKit, pooled contexts, smart wait strategies.",
    tags: ["playwright", "chromium"],
    accent: "lime" as const,
  },
  {
    n: "06",
    title: "output you can use",
    body: "JSON, JSONL, Parquet, plain text. Stream millions of pages or load straight into pandas — no bespoke schema.",
    tags: ["jsonl", "parquet"],
    accent: "cyan" as const,
  },
];

const accentRing: Record<"lime" | "cyan" | "amber" | "magenta", string> = {
  lime: "group-hover:border-lime/40 group-hover:shadow-[0_24px_48px_-24px_hsl(var(--lime)/0.3)]",
  cyan: "group-hover:border-cyan/40 group-hover:shadow-[0_24px_48px_-24px_hsl(var(--cyan)/0.3)]",
  amber: "group-hover:border-amber/40 group-hover:shadow-[0_24px_48px_-24px_hsl(var(--amber)/0.3)]",
  magenta: "group-hover:border-magenta/40 group-hover:shadow-[0_24px_48px_-24px_hsl(var(--magenta)/0.3)]",
};
const accentText: Record<"lime" | "cyan" | "amber" | "magenta", string> = {
  lime: "text-lime",
  cyan: "text-cyan",
  amber: "text-amber",
  magenta: "text-magenta",
};

const tickerItems = [
  "v0.1.0",
  "134 / 134 tests passing",
  "3,164 LOC",
  "MIT licensed",
  "Python 3.11+",
  "async / await",
  "S3-ready",
  "playwright optional",
];

export default function Landing() {
  return (
    <div className="min-h-screen flex flex-col relative">
      <TopBar />

      {/* ── Hero ───────────────────────────────────────────── */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="absolute inset-0 bg-mesh" />
        <div className="absolute inset-0 grid-pattern opacity-60" />

        {/* status ticker */}
        <div className="relative border-b border-border/60 bg-background/40 backdrop-blur-sm">
          <div className="flex overflow-hidden whitespace-nowrap py-2">
            <div className="flex shrink-0 animate-ticker">
              {[...tickerItems, ...tickerItems, ...tickerItems].map((item, i) => (
                <span
                  key={i}
                  className="meta-pill px-6 flex items-center gap-3 shrink-0"
                >
                  {i % tickerItems.length === 0 && (
                    <span className="live-dot" />
                  )}
                  {item}
                  <span className="text-border-strong">/</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="relative mx-auto max-w-7xl px-6 lg:px-10 pt-20 pb-24 lg:pt-28 lg:pb-32">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 items-center">
            {/* Left column: editorial display + CTAs */}
            <div className="lg:col-span-7 space-y-8 animate-fade-up">
              <div className="flex items-center gap-3">
                <span className="meta-pill">
                  <span className="live-dot" />
                  the public data crawler
                </span>
              </div>

              <h1 className="font-display tracking-tight">
                <span className="block text-display-xl font-extrabold leading-[0.88] text-foreground">
                  yoink<span className="text-lime">.</span>
                </span>
                <span className="block mt-3 text-2xl md:text-3xl font-medium italic text-muted-foreground tracking-tight max-w-2xl">
                  fast, async, polite —{" "}
                  <span className="text-foreground/85 not-italic font-semibold">
                    extract clean data
                  </span>{" "}
                  from any public website.
                </span>
              </h1>

              <p className="text-base md:text-lg text-muted-foreground leading-relaxed max-w-xl">
                A focused Python crawler with rate limiting, robots.txt
                compliance, JS rendering, and resumable S3 checkpoints.
                ~3,200 lines, 134 tests, zero ceremony.
              </p>

              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <Button asChild variant="lime" size="lg">
                  <Link to="/docs/quickstart">
                    Get started
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 12h14M13 6l6 6-6 6"
                      />
                    </svg>
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg">
                  <a
                    href="https://github.com/ErikkJs/yoink"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor" className="size-4">
                      <path
                        fillRule="evenodd"
                        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                        clipRule="evenodd"
                      />
                    </svg>
                    github.com/ErikkJs/yoink
                  </a>
                </Button>
              </div>
            </div>

            {/* Right column: terminal block */}
            <div className="lg:col-span-5 animate-fade-up [animation-delay:120ms]">
              <TerminalCard />
            </div>
          </div>
        </div>
      </section>

      {/* ── Feature grid ──────────────────────────────────── */}
      <section className="relative">
        <div className="mx-auto max-w-7xl px-6 lg:px-10 py-24">
          <div className="flex items-end justify-between flex-wrap gap-4 mb-14">
            <div>
              <p className="meta-pill text-lime mb-3">▸ what's in the box</p>
              <h2 className="font-display text-display-md font-bold tracking-tight max-w-3xl">
                Everything you need.{" "}
                <span className="italic text-muted-foreground">
                  Nothing you don't.
                </span>
              </h2>
            </div>
            <p className="font-mono text-xs text-muted-foreground max-w-xs">
              ~3,200 lines of focused Python.
              <br />
              The rest is battle-tested libraries.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-border-strong/40 rounded-2xl overflow-hidden border border-border-strong/40">
            {features.map((f) => (
              <article
                key={f.n}
                className={`group relative bg-background hover:bg-card/50 p-7 transition-all border border-transparent ${accentRing[f.accent]}`}
              >
                <div className="flex items-start justify-between mb-5">
                  <span className={`font-mono text-[0.7rem] uppercase tracking-[0.18em] ${accentText[f.accent]}`}>
                    {f.n} ─
                  </span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className={`size-3.5 opacity-0 group-hover:opacity-100 transition-opacity ${accentText[f.accent]}`}>
                    <path strokeLinecap="round" strokeWidth={2} d="M7 17L17 7M17 7H8M17 7V16" />
                  </svg>
                </div>
                <h3 className="font-display text-xl font-semibold tracking-tight mb-3 text-foreground">
                  {f.title}
                </h3>
                <p className="text-[0.92rem] text-muted-foreground leading-relaxed mb-5">
                  {f.body}
                </p>
                <div className="flex flex-wrap gap-1.5 pt-4 border-t border-border/60">
                  {f.tags.map((t) => (
                    <span
                      key={t}
                      className="font-mono text-[0.65rem] text-muted-foreground/80 px-1.5 py-0.5 rounded bg-muted/40 border border-border"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pipeline diagram ─────────────────────────────── */}
      <section className="relative border-y border-border bg-card/20">
        <div className="mx-auto max-w-7xl px-6 lg:px-10 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-5">
              <p className="meta-pill text-lime mb-3">▸ how it works</p>
              <h2 className="font-display text-display-md font-bold tracking-tight mb-5">
                One pipeline.{" "}
                <span className="italic text-muted-foreground">
                  Twelve modules.
                </span>
              </h2>
              <p className="text-muted-foreground leading-relaxed mb-6">
                Each module does one thing. The crawler is the conductor.
                Swap the fetcher, storage backend, or extractor without
                forking — every seam is an interface, not magic.
              </p>
              <Link
                to="/docs/concepts/architecture"
                className="inline-flex items-center gap-2 text-sm text-lime hover:text-lime-bright transition-colors group"
              >
                Architecture deep-dive
                <span className="transition-transform group-hover:translate-x-1">→</span>
              </Link>
            </div>

            <div className="lg:col-span-7">
              <PipelineDiagram />
            </div>
          </div>
        </div>
      </section>

      {/* ── Use cases ────────────────────────────────────── */}
      <section className="relative">
        <div className="mx-auto max-w-7xl px-6 lg:px-10 py-24">
          <div className="text-center mb-14 max-w-2xl mx-auto">
            <p className="meta-pill text-lime mb-3 justify-center inline-flex">▸ used for</p>
            <h2 className="font-display text-display-md font-bold tracking-tight">
              Public data is public.{" "}
              <span className="italic text-muted-foreground">
                Treat it that way.
              </span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-border-strong/40 rounded-2xl overflow-hidden border border-border-strong/40">
            {[
              {
                t: "AI / RAG datasets",
                d: "Crawl docs sites, mirror knowledge bases, build embedding indexes — clean text out, no boilerplate.",
              },
              {
                t: "Lambda crawlers",
                d: "S3 checkpoints + 14-min budget = crawls that survive across invocations indefinitely.",
              },
              {
                t: "Content analysis",
                d: "Parquet output drops straight into pandas / DuckDB / Athena. No schema gymnastics.",
              },
            ].map((u) => (
              <div
                key={u.t}
                className="bg-background p-8 hover:bg-card/40 transition-colors"
              >
                <h3 className="font-display text-xl font-semibold tracking-tight mb-2">
                  {u.t}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {u.d}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────── */}
      <section className="relative border-t border-border overflow-hidden">
        <div className="absolute inset-0 bg-mesh opacity-50" />
        <div className="relative mx-auto max-w-4xl px-6 lg:px-10 py-24 text-center">
          <h2 className="font-display text-display-md font-bold tracking-tight mb-4">
            Ready to <span className="italic text-lime">yoink</span>?
          </h2>
          <p className="text-muted-foreground mb-8 max-w-xl mx-auto leading-relaxed">
            One pip install. Zero config required. Read the quickstart and
            have a crawl running before your coffee gets cold.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button asChild variant="lime" size="lg">
              <Link to="/docs/quickstart">Quickstart →</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link to="/docs/api/crawler">API reference</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────── */}
      <footer className="border-t border-border">
        <div className="mx-auto max-w-7xl px-6 lg:px-10 py-12">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-10">
            <div className="col-span-2">
              <Link to="/" className="inline-flex items-baseline gap-2 group">
                <span className="font-display text-2xl font-bold italic group-hover:text-lime transition-colors">
                  yoink<span className="text-lime">.</span>
                </span>
              </Link>
              <p className="text-sm text-muted-foreground mt-3 max-w-xs leading-relaxed">
                The public data crawler. Built for people who'd rather ship a
                pipeline than tune a spider.
              </p>
            </div>

            <FooterCol
              title="Docs"
              links={[
                { label: "Introduction", to: "/docs/introduction" },
                { label: "Quickstart", to: "/docs/quickstart" },
                { label: "Architecture", to: "/docs/concepts/architecture" },
              ]}
            />
            <FooterCol
              title="Reference"
              links={[
                { label: "CLI", to: "/docs/cli/crawl" },
                { label: "Python API", to: "/docs/api/crawler" },
                { label: "Examples", to: "/docs/examples/basic" },
              ]}
            />
            <FooterCol
              title="External"
              links={[
                { label: "GitHub ↗", href: "https://github.com/ErikkJs/yoink" },
                {
                  label: "Issues ↗",
                  href: "https://github.com/ErikkJs/yoink/issues",
                },
              ]}
            />
          </div>

          {/* Bottom bar */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-3 pt-6 border-t border-border">
            <p className="font-mono text-[0.7rem] text-muted-foreground">
              <span className="text-lime">▸</span> yoink/0.1.0 · MIT · 134
              tests · 3,164 LOC · Python 3.11+
            </p>
            <p className="font-mono text-[0.7rem] text-muted-foreground/60">
              built by{" "}
              <a
                href="https://github.com/ErikkJs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-foreground/80 hover:text-lime transition-colors"
              >
                @ErikkJs
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FooterCol({
  title,
  links,
}: {
  title: string;
  links: { label: string; to?: string; href?: string }[];
}) {
  return (
    <div>
      <p className="meta-pill mb-4">{title}</p>
      <ul className="space-y-2">
        {links.map((l) => (
          <li key={l.label}>
            {l.to ? (
              <Link
                to={l.to}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {l.label}
              </Link>
            ) : (
              <a
                href={l.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {l.label}
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ── Terminal card ───────────────────────────────────── */
function TerminalCard() {
  return (
    <div className="relative">
      {/* lime glow behind */}
      <div className="absolute -inset-4 bg-gradient-to-br from-lime/10 via-transparent to-cyan/5 blur-2xl rounded-2xl pointer-events-none" />

      <div className="relative rounded-xl border border-border-strong bg-card/80 backdrop-blur-sm overflow-hidden shadow-2xl">
        {/* Title bar */}
        <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-card/60">
          <div className="flex items-center gap-1.5">
            <span className="size-2.5 rounded-full bg-destructive/70" />
            <span className="size-2.5 rounded-full bg-amber/80" />
            <span className="size-2.5 rounded-full bg-lime/80" />
          </div>
          <span className="font-mono text-[0.65rem] text-muted-foreground/70">
            ~/yoink — zsh
          </span>
          <span className="font-mono text-[0.65rem] text-lime flex items-center gap-1">
            <span className="size-1.5 rounded-full bg-lime animate-pulse" />
            live
          </span>
        </div>

        {/* Content */}
        <pre className="p-5 text-[0.78rem] leading-[1.7] overflow-x-auto bg-[hsl(var(--code-bg))] font-mono">
          <code>
            <span className="text-muted-foreground/60"># Install</span>
            {"\n"}
            <span className="text-lime">$</span> pip install yoink
            {"\n\n"}
            <span className="text-muted-foreground/60"># Crawl &amp; save JSONL</span>
            {"\n"}
            <span className="text-lime">$</span> yoink crawl{" "}
            <span className="text-cyan">https://docs.example.com</span>{" "}
            <span className="text-amber">--depth</span> 2{" "}
            <span className="text-amber">-o</span> data.jsonl
            {"\n"}
            <span className="text-muted-foreground">  Yoinking pages: </span>
            <span className="text-lime">100%</span>
            <span className="text-muted-foreground"> ████████ 87/100</span>
            {"\n"}
            <span className="text-muted-foreground/70">  ╰─►</span>{" "}
            <span className="text-foreground">Yoinked 87 pages → data.jsonl</span>
            {"\n\n"}
            <span className="text-muted-foreground/60"># Analyze</span>
            {"\n"}
            <span className="text-lime">$</span> yoink stats data.jsonl{" "}
            <span className="text-amber">--json</span>{" "}
            <span className="text-muted-foreground">|</span> jq{" "}
            <span className="text-cyan">'.top_domains'</span>
            {"\n"}
            <span className="text-lime inline-block animate-type-cursor">▊</span>
          </code>
        </pre>
      </div>
    </div>
  );
}

/* ── Pipeline diagram ───────────────────────────────── */
function PipelineDiagram() {
  const stages = [
    { label: "Scheduler", sub: "queue / dedup", color: "lime" as const },
    { label: "RateLimiter", sub: "token bucket", color: "amber" as const },
    { label: "Robots", sub: "is_allowed", color: "amber" as const },
    { label: "Fetcher", sub: "aiohttp / playwright", color: "cyan" as const },
    { label: "Parser", sub: "links / metadata", color: "magenta" as const },
    { label: "Extractor", sub: "trafilatura", color: "magenta" as const },
    { label: "Checkpoint", sub: "JSONL / S3", color: "lime" as const },
  ];

  const colorMap = {
    lime: "border-lime/40 text-lime",
    amber: "border-amber/40 text-amber",
    cyan: "border-cyan/40 text-cyan",
    magenta: "border-magenta/40 text-magenta",
  };

  return (
    <div className="relative">
      <div className="rounded-2xl border border-border-strong bg-background/80 backdrop-blur p-6">
        <div className="flex items-center justify-between mb-4">
          <span className="meta-pill">crawl pipeline</span>
          <span className="font-mono text-[0.65rem] text-muted-foreground/70">
            crawler.py
          </span>
        </div>

        <div className="space-y-1.5">
          {stages.map((s, i) => (
            <div
              key={s.label}
              className={`flex items-center gap-3 group rounded-md px-3 py-2 hover:bg-muted/40 transition-colors border-l-2 ${colorMap[s.color]} bg-muted/10`}
            >
              <span className="font-mono text-[0.65rem] text-muted-foreground/60 w-6">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="flex-1 flex items-baseline justify-between gap-3">
                <span className="font-display font-semibold">{s.label}</span>
                <span className="font-mono text-[0.7rem] text-muted-foreground">
                  {s.sub}
                </span>
              </div>
              {i < stages.length - 1 && (
                <span className="text-muted-foreground/40 font-mono text-xs">↓</span>
              )}
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
          <span className="font-mono text-[0.65rem] text-muted-foreground">
            workers: <span className="text-lime">N</span>
          </span>
          <span className="font-mono text-[0.65rem] text-muted-foreground">
            output: <span className="text-cyan">JSONL/Parquet/...</span>
          </span>
        </div>
      </div>
    </div>
  );
}
