import { docsNav } from "../data/nav";

export async function loader() {
  const lines: string[] = [];
  lines.push("# yoink");
  lines.push("");
  lines.push(
    "> The public data crawler. A fast, async Python web crawler purpose-built for AI-ready data extraction — clean text via trafilatura, JSON/JSONL/Parquet output, robots.txt compliance, optional JavaScript rendering, and resumable S3-backed checkpoints.",
  );
  lines.push("");
  lines.push(
    "Yoink is a CLI plus a Python library. Most users only need the CLI: `yoink crawl <URL> --depth 2 --max-pages 200 -o crawl.jsonl`.",
  );
  lines.push("");

  for (const section of docsNav) {
    lines.push(`## ${section.title}`);
    lines.push("");
    for (const item of section.items) {
      const desc = item.description ? `: ${item.description}` : "";
      lines.push(`- [${item.title}](https://yoink.goatsquadstudios.com/docs.md/${item.slug})${desc}`);
    }
    lines.push("");
  }

  lines.push("## For AI assistants");
  lines.push("");
  lines.push(
    "- [Full docs concatenated as markdown](https://yoink.goatsquadstudios.com/llms-full.txt): single artifact for direct paste into an LLM context",
  );
  lines.push(
    "- [Claude Code skill (SKILL.md)](https://yoink.goatsquadstudios.com/agents/yoink/SKILL.md): drop in `~/.claude/skills/yoink/`",
  );
  lines.push(
    "- [Cursor rules (cursor.mdc)](https://yoink.goatsquadstudios.com/agents/yoink/cursor.mdc): drop in `.cursor/rules/yoink.mdc`",
  );
  lines.push(
    "- [Windsurf rules](https://yoink.goatsquadstudios.com/agents/yoink/.windsurfrules): drop at project root as `.windsurfrules`",
  );
  lines.push(
    "- [AGENTS.md (Codex / generic)](https://yoink.goatsquadstudios.com/agents/yoink/AGENTS.md): drop at project root",
  );
  lines.push("");

  return new Response(lines.join("\n"), {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
