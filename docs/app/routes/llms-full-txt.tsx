import { docsNav } from "../data/nav";
import {
  extractFrontmatterFields,
  getRawDoc,
  stripFrontmatter,
} from "../lib/docs-raw.server";

export async function loader() {
  const parts: string[] = [];
  parts.push("# yoink — full documentation");
  parts.push("");
  parts.push(
    "> Fast, async Python web crawler with rate limiting, robots.txt compliance, optional JavaScript rendering, and resumable S3-backed checkpoints. This file concatenates every documentation page so you can paste the whole thing into an AI assistant's context.",
  );
  parts.push("");

  for (const section of docsNav) {
    parts.push(`---`);
    parts.push("");
    parts.push(`# ${section.title}`);
    parts.push("");
    for (const item of section.items) {
      const raw = getRawDoc(item.slug);
      if (raw === null) continue;
      const front = extractFrontmatterFields(raw);
      const body = stripFrontmatter(raw).trim();
      parts.push(`## ${front.title ?? item.title}`);
      parts.push("");
      parts.push(
        `_Source: \`docs/${item.slug}.mdx\` · https://yoink.goatsquadstudios.com/docs/${item.slug}_`,
      );
      parts.push("");
      if (front.description) {
        parts.push(`> ${front.description}`);
        parts.push("");
      }
      parts.push(body);
      parts.push("");
    }
  }

  return new Response(parts.join("\n"), {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
