export interface NavItem {
  title: string;
  slug: string;
  description?: string;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const docsNav: NavSection[] = [
  {
    title: "Getting started",
    items: [
      {
        title: "Introduction",
        slug: "introduction",
        description: "What yoink is and why it exists",
      },
      {
        title: "Installation",
        slug: "installation",
        description: "Install yoink and its optional extras",
      },
      {
        title: "Quickstart",
        slug: "quickstart",
        description: "Yoink your first website in 30 seconds",
      },
    ],
  },
  {
    title: "Concepts",
    items: [
      {
        title: "Architecture",
        slug: "concepts/architecture",
        description: "How the pieces fit together",
      },
      {
        title: "Rate limiting",
        slug: "concepts/rate-limiting",
        description: "Per-domain token bucket and crawl-delay",
      },
      {
        title: "robots.txt",
        slug: "concepts/robots-txt",
        description: "Compliance, parsing, and matching",
      },
      {
        title: "JavaScript rendering",
        slug: "concepts/javascript-rendering",
        description: "Crawling SPAs with Playwright",
      },
      {
        title: "Checkpointing",
        slug: "concepts/checkpointing",
        description: "Resumable crawls with local or S3 storage",
      },
      {
        title: "URL filtering",
        slug: "concepts/url-filtering",
        description: "Include, exclude, extension, and domain filters",
      },
    ],
  },
  {
    title: "CLI",
    items: [
      {
        title: "yoink crawl",
        slug: "cli/crawl",
        description: "All flags for the primary command",
      },
      {
        title: "yoink stats",
        slug: "cli/stats",
        description: "Analyze a saved crawl",
      },
      {
        title: "yoink version",
        slug: "cli/version",
        description: "Show version info",
      },
    ],
  },
  {
    title: "Python API",
    items: [
      { title: "Crawler", slug: "api/crawler" },
      { title: "CrawlConfig", slug: "api/config" },
      { title: "Page", slug: "api/page" },
      { title: "CheckpointManager", slug: "api/checkpoint" },
      { title: "Filters", slug: "api/filters" },
      { title: "Storage backends", slug: "api/storage" },
      { title: "Stats", slug: "api/stats" },
      { title: "Writers", slug: "api/writers" },
    ],
  },
  {
    title: "Examples",
    items: [
      { title: "Basic crawl", slug: "examples/basic" },
      { title: "AI training data", slug: "examples/ai-training" },
      { title: "Checkpoint & resume", slug: "examples/checkpoint-resume" },
      { title: "Lambda + S3 checkpoints", slug: "examples/lambda-s3" },
      { title: "Custom extraction", slug: "examples/custom-extraction" },
    ],
  },
  {
    title: "Reference",
    items: [
      { title: "Output formats", slug: "reference/output-formats" },
      { title: "Configuration", slug: "reference/configuration" },
    ],
  },
];

export function flattenNav(): NavItem[] {
  return docsNav.flatMap((section) => section.items);
}

export function findNavItem(slug: string): {
  item: NavItem;
  section: NavSection;
  prev: NavItem | null;
  next: NavItem | null;
} | null {
  const flat = flattenNav();
  const index = flat.findIndex((i) => i.slug === slug);
  if (index === -1) return null;

  const item = flat[index];
  const section = docsNav.find((s) => s.items.some((i) => i.slug === slug))!;

  return {
    item,
    section,
    prev: index > 0 ? flat[index - 1] : null,
    next: index < flat.length - 1 ? flat[index + 1] : null,
  };
}
