import type { Tool } from "./tools";
import { getToolMeta } from "./tools";

export type RecipeIcon =
  | "install"
  | "mirror"
  | "training"
  | "spa"
  | "watch"
  | "lambda";

export interface Recipe {
  id: string;
  title: string;
  description: string;
  icon: RecipeIcon;
  prompt: (tool: Tool) => string;
}

function preamble(tool: Tool): string {
  const meta = getToolMeta(tool);
  switch (tool) {
    case "claude":
      return `Use the yoink skill at ${meta.installPath}.`;
    case "cursor":
      return `Follow the yoink rules at ${meta.installPath}.`;
    case "windsurf":
      return `Follow the yoink section of ${meta.installPath}.`;
    case "codex":
      return `Per ${meta.installPath} (yoink section):`;
  }
}

function build(tool: Tool, body: string): string {
  return `${preamble(tool)}\n\n${body.trim()}\n`;
}

export const RECIPES: Recipe[] = [
  {
    id: "install",
    title: "Install yoink in this project",
    description:
      "Adds yoink to the active Python environment, verifies the CLI works, and warns about the PyPI name collision.",
    icon: "install",
    prompt: (tool) =>
      build(
        tool,
        `Install yoink in this project, then run \`yoink version\` and show me the output.

Notes for you:
- Do NOT run \`pip install yoink\` — a different package on PyPI owns that name.
- Use \`pip install "yoink @ git+https://github.com/ErikkJs/yoink.git"\`.
- If \`pyproject.toml\` exists, add it there instead of a bare \`pip install\`.
- If we also need Parquet / S3 / JavaScript rendering, install the matching extras: \`[parquet]\`, \`[s3]\`, \`[browser]\`, or \`[all]\`. For \`[browser]\` also run \`playwright install chromium\`.`,
      ),
  },
  {
    id: "mirror-docs",
    title: "Mirror a documentation site",
    description:
      "Crawls a docs site to clean JSONL with checkpoint-resume, ready for embedding or full-text search.",
    icon: "mirror",
    prompt: (tool) =>
      build(
        tool,
        `Use yoink to mirror the documentation at <PASTE URL HERE>.

Command to run:
\`\`\`
yoink crawl <PASTE URL HERE> \\
  --depth 3 \\
  --max-pages 1000 \\
  --include "*/docs/*" \\
  --skip-extensions pdf,zip \\
  --format jsonl \\
  --checkpoint mirror.jsonl --resume \\
  -o mirror.jsonl
\`\`\`

After it finishes, run \`yoink stats mirror.jsonl\` and summarize the result — pages crawled, depth distribution, status codes. If the site is JS-heavy (empty page bodies in the result), add \`--render-js\` and re-run.`,
      ),
  },
  {
    id: "ai-training",
    title: "Build an AI training dataset",
    description:
      "Crawls, extracts clean text, writes Parquet, then dedupes by text hash. Ready for pandas / DuckDB / a model trainer.",
    icon: "training",
    prompt: (tool) =>
      build(
        tool,
        `Build a small training dataset from <PASTE URL HERE>.

Steps:
1. Crawl with \`yoink crawl <URL> --depth 2 --max-pages 500 --format parquet -o raw.parquet\`. Install the \`[parquet]\` extra if it's not already there.
2. Open raw.parquet in Python:
   - drop rows where \`text\` is null or shorter than 200 characters
   - drop duplicates by a hash of the cleaned \`text\` column
   - write the result to training.parquet
3. Print: number of pages before, number after dedup, average text length, and the top 5 URL paths.`,
      ),
  },
  {
    id: "spa",
    title: "Scrape a JavaScript-heavy SPA",
    description:
      "Installs the browser extra, drives Playwright with a sensible wait strategy for SPAs.",
    icon: "spa",
    prompt: (tool) =>
      build(
        tool,
        `The site at <PASTE URL HERE> is a JavaScript SPA — plain HTTP returns an empty shell. Use yoink with Playwright.

Steps:
1. Install the browser extra: \`pip install "yoink[browser] @ git+https://github.com/ErikkJs/yoink.git"\` then \`playwright install chromium\`.
2. Crawl with:
\`\`\`
yoink crawl <URL> \\
  --render-js \\
  --wait-for networkidle \\
  --depth 2 \\
  --max-pages 200 \\
  -o spa.jsonl
\`\`\`
3. If pages still look incomplete, add \`--wait-selector ".content-loaded"\` (or whatever marker the site uses to signal "ready") and re-run.`,
      ),
  },
  {
    id: "watch",
    title: "Watch a site for changes",
    description:
      "Sets up a daily re-crawl, diffs against the previous run, and reports the delta.",
    icon: "watch",
    prompt: (tool) =>
      build(
        tool,
        `Set up a daily watcher for <PASTE URL HERE>.

What I want:
1. A shell script \`watch.sh\` that runs \`yoink crawl <URL> --checkpoint watch.jsonl --resume --max-pages 1000 -o today.jsonl\`, then renames today.jsonl to dated/$(date +%F).jsonl.
2. A Python script \`diff.py\` that loads today's and yesterday's JSONL files, compares pages by URL + sha256(text), and prints added / removed / changed URLs.
3. A cron entry that runs watch.sh && diff.py at 06:00 daily.

Keep the script idempotent so if it runs twice in one day the second run is a no-op.`,
      ),
  },
  {
    id: "lambda-s3",
    title: "Crawl from AWS Lambda with S3 checkpoints",
    description:
      "Lambda handler that survives 15-minute timeouts via S3 checkpoint + self-reinvoke. Includes IAM policy.",
    icon: "lambda",
    prompt: (tool) =>
      build(
        tool,
        `Scaffold an AWS Lambda crawler.

Requirements:
1. Install yoink with the \`[s3]\` extra in the Lambda's Python environment.
2. Handler runs \`yoink crawl <event.url> --checkpoint s3://<bucket>/crawl.jsonl --resume --max-pages 1000\` with a 14-minute internal time budget.
3. If the crawl isn't done when the budget elapses, the handler invokes itself again with the same event (boto3 Lambda Invoke, type=Event).
4. Produce:
   - the handler code
   - an IAM policy granting \`s3:GetObject\`, \`s3:PutObject\`, \`s3:HeadObject\` on the bucket and \`lambda:InvokeFunction\` on the function itself
   - a SAM / CDK / Terraform snippet (pick whichever is in the project already, or default to SAM)`,
      ),
  },
];
