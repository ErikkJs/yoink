/**
 * Build-time search index over all MDX docs.
 *
 * Indexes each doc's frontmatter (title, description) plus its section
 * from `nav.ts`. The MDX plugin owns the `.mdx` import path, so we can't
 * easily get raw text for full-content search — frontmatter + section +
 * curated keywords gives us a workable cmd-k palette without that.
 *
 * If full-content search becomes important later, a Vite plugin that
 * emits a `search-index.json` next to each MDX is the right next step.
 */

import { docsNav, type NavItem, type NavSection } from "../data/nav";

interface MDXFrontmatter {
  title?: string;
  description?: string;
  category?: string;
}

interface MDXModule {
  frontmatter?: MDXFrontmatter;
}

const docModules = import.meta.glob<MDXModule>(
  "../content/docs/**/*.mdx",
  { eager: true }
);

export interface SearchEntry {
  slug: string;
  title: string;
  description: string;
  section: string;
  /** Free-form keywords used for matching that aren't in title/description. */
  keywords: string[];
}

export type SearchHitMatch =
  | { type: "title"; text: string }
  | { type: "description"; text: string }
  | { type: "keyword"; text: string };

export interface SearchHit {
  entry: SearchEntry;
  score: number;
  match: SearchHitMatch;
}

function pathToSlug(path: string): string {
  return path.replace("../content/docs/", "").replace(/\.mdx$/, "");
}

/**
 * Per-doc keyword list. Each entry contributes to matching but is not
 * shown in the UI verbatim — they help lead users to the right page
 * when they type something the title doesn't say (e.g. "cmd-k", "ctrl-k",
 * "lambda", "aws", "playwright", "spa").
 */
const keywordsBySlug: Record<string, string[]> = {
  introduction: ["overview", "intro", "what is yoink", "what's in the box"],
  installation: ["install", "pip", "poetry", "pyproject", "extras", "playwright"],
  quickstart: ["getting started", "first crawl", "hello world"],

  "concepts/architecture": [
    "modules",
    "fetcher",
    "parser",
    "extractor",
    "scheduler",
    "lifecycle",
    "internals",
  ],
  "concepts/rate-limiting": [
    "rps",
    "requests per second",
    "throttle",
    "burst",
    "token bucket",
    "crawl-delay",
    "request-delay",
  ],
  "concepts/robots-txt": [
    "robots",
    "user-agent",
    "allow",
    "disallow",
    "sitemap",
    "ethics",
  ],
  "concepts/javascript-rendering": [
    "spa",
    "react",
    "vue",
    "playwright",
    "headless",
    "browser",
    "chromium",
    "firefox",
    "webkit",
    "render js",
    "single page app",
  ],
  "concepts/checkpointing": [
    "resume",
    "lambda",
    "s3",
    "checkpoint",
    "save state",
    "fault tolerance",
    "interrupt",
  ],
  "concepts/url-filtering": [
    "include",
    "exclude",
    "glob",
    "regex",
    "skip",
    "extension",
    "domain allowlist",
    "filter pipeline",
  ],

  "cli/crawl": [
    "command",
    "command line",
    "shell",
    "flags",
    "options",
    "--depth",
    "--include",
    "--rate-limit",
  ],
  "cli/stats": ["statistics", "metrics", "analyze", "csv export", "jq"],
  "cli/version": ["--version", "version flag"],

  "api/crawler": ["python api", "Crawler class", "asyncio", "crawl()"],
  "api/config": ["CrawlConfig", "settings", "options", "configuration"],
  "api/page": ["Page model", "data shape", "pydantic"],
  "api/checkpoint": ["CheckpointManager", "from_uri", "resume"],
  "api/filters": [
    "URLFilter",
    "DomainFilter",
    "CombinedFilter",
    "from_config",
  ],
  "api/storage": [
    "CheckpointStorage",
    "LocalFileStorage",
    "S3Storage",
    "StorageFactory",
    "iam",
    "aws",
  ],
  "api/stats": ["CrawlStats", "compute", "format_summary", "export_csv"],
  "api/writers": [
    "Writer",
    "write_json",
    "write_jsonl",
    "write_parquet",
    "write_text",
  ],

  "examples/basic": ["hello world", "first crawl"],
  "examples/ai-training": [
    "training data",
    "embeddings",
    "rag",
    "llm",
    "fine-tune",
    "dedupe",
  ],
  "examples/checkpoint-resume": ["resumable", "lambda", "s3"],
  "examples/lambda-s3": ["aws", "lambda", "eventbridge", "iam", "deployment"],
  "examples/custom-extraction": [
    "subclass",
    "extractor",
    "json-ld",
    "schema.org",
    "pdf",
    "markdown",
  ],

  "reference/output-formats": ["json", "jsonl", "parquet", "text", "schema"],
  "reference/configuration": ["all options", "knobs", "cli mapping"],
};

function buildIndex(): SearchEntry[] {
  const sectionBySlug = new Map<string, string>();
  for (const sec of docsNav as NavSection[]) {
    for (const item of sec.items as NavItem[]) {
      sectionBySlug.set(item.slug, sec.title);
    }
  }

  const entries: SearchEntry[] = [];
  for (const [path, mod] of Object.entries(docModules)) {
    const slug = pathToSlug(path);
    const fm = mod?.frontmatter ?? {};
    entries.push({
      slug,
      title: fm.title || slug,
      description: fm.description || "",
      section: sectionBySlug.get(slug) || fm.category || "Docs",
      keywords: keywordsBySlug[slug] || [],
    });
  }
  return entries;
}

export const searchIndex: SearchEntry[] = buildIndex();

/**
 * Score one entry against a query. Weights:
 *   - exact title:        1000
 *   - title startsWith:    600
 *   - title contains:      400
 *   - keyword exact:       300
 *   - keyword contains:    200
 *   - description:          80
 *   - section:              60
 *
 * Returns null if nothing matched.
 */
function scoreEntry(entry: SearchEntry, q: string): SearchHit | null {
  const ql = q.toLowerCase();
  const tl = entry.title.toLowerCase();
  const dl = entry.description.toLowerCase();
  const sl = entry.section.toLowerCase();

  let score = 0;
  let match: SearchHitMatch | null = null;

  if (tl === ql) {
    score += 1000;
    match = { type: "title", text: entry.title };
  } else if (tl.startsWith(ql)) {
    score += 600;
    match = { type: "title", text: entry.title };
  } else if (tl.includes(ql)) {
    score += 400;
    match = { type: "title", text: entry.title };
  }

  for (const kw of entry.keywords) {
    const kwl = kw.toLowerCase();
    if (kwl === ql) {
      score += 300;
      if (!match) match = { type: "keyword", text: kw };
    } else if (kwl.includes(ql) || ql.includes(kwl)) {
      score += 200;
      if (!match) match = { type: "keyword", text: kw };
    }
  }

  if (dl.includes(ql)) {
    score += 80;
    if (!match) match = { type: "description", text: entry.description };
  }

  if (sl.includes(ql)) {
    score += 60;
    if (!match) match = { type: "title", text: entry.title };
  }

  if (score === 0 || !match) return null;
  return { entry, score, match };
}

export function search(query: string, limit = 8): SearchHit[] {
  const ql = query.trim();
  if (!ql) return [];
  const hits = searchIndex
    .map((e) => scoreEntry(e, ql))
    .filter((h): h is SearchHit => h !== null)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
  return hits;
}

/** Highlight matched substring inside `text`. */
export function highlightSegments(
  text: string,
  query: string
): { text: string; match: boolean }[] {
  const ql = query.toLowerCase();
  if (!ql) return [{ text, match: false }];
  const segments: { text: string; match: boolean }[] = [];
  const tl = text.toLowerCase();
  let i = 0;
  while (i < text.length) {
    const next = tl.indexOf(ql, i);
    if (next === -1) {
      segments.push({ text: text.slice(i), match: false });
      break;
    }
    if (next > i) segments.push({ text: text.slice(i, next), match: false });
    segments.push({ text: text.slice(next, next + ql.length), match: true });
    i = next + ql.length;
  }
  return segments;
}
