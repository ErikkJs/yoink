// Raw MDX access — used by /llms.txt, /llms-full.txt, and the
// "Copy as Markdown" button on each docs page.
//
// Why this file imports a generated module: we want the *source text* of each
// MDX file as a plain string. `import.meta.glob('**/*.mdx', { query: '?raw' })`
// looks like it should give us that, but @mdx-js/rollup's transform hook does
// not respect the `?raw` query — it processes every .mdx import regardless,
// so `eager: true` returns compiled MDX modules, not strings.
//
// Workaround: a build-time script reads the .mdx files with fs and emits
// `docs-raw-data.ts` containing a typed string map. That file is imported
// here and is also referenced by the docs page route to serve raw markdown.
// Generator runs as `predev` and `prebuild` (see package.json).

import { RAW_DOCS } from "./docs-raw-data";

export interface RawDoc {
  slug: string;
  raw: string;
}

export function getRawDoc(slug: string): string | null {
  return RAW_DOCS[slug] ?? null;
}

export function listRawDocs(): RawDoc[] {
  return Object.entries(RAW_DOCS).map(([slug, raw]) => ({ slug, raw }));
}

// Strips the leading YAML frontmatter block (--- ... ---) from an MDX source
// string. Returns the body verbatim, including any MDX expressions / JSX. The
// frontmatter values are exposed via the compiled module elsewhere
// (docs.server.ts); for llms-full.txt we want the prose only.
export function stripFrontmatter(raw: string): string {
  const match = raw.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/);
  if (!match) return raw;
  return raw.slice(match[0].length);
}

// Quick frontmatter extractor — only pulls `title` and `description`, which is
// all we need for the llms-full.txt headers. Avoids pulling in a YAML parser.
export function extractFrontmatterFields(raw: string): {
  title?: string;
  description?: string;
} {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) return {};
  const body = match[1];
  const out: { title?: string; description?: string } = {};
  for (const line of body.split(/\r?\n/)) {
    const m = line.match(/^(title|description):\s*(.*)$/);
    if (!m) continue;
    let value = m[2].trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    out[m[1] as "title" | "description"] = value;
  }
  return out;
}
