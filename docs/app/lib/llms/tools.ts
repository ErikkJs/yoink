export type Tool = "claude" | "cursor" | "windsurf" | "codex";

export interface ToolMeta {
  id: Tool;
  label: string;
  shortLabel: string;
  installPath: string;
  artifactFile: string;
  artifactLabel: string;
  installHint: string;
  downloadUrl: string;
}

export const TOOLS: ToolMeta[] = [
  {
    id: "claude",
    label: "Claude Code",
    shortLabel: "Claude",
    installPath: "~/.claude/skills/yoink/SKILL.md",
    artifactFile: "SKILL.md",
    artifactLabel: "SKILL.md",
    installHint:
      "Save SKILL.md to ~/.claude/skills/yoink/. Claude Code will autoload the skill when you say things like “scrape” or “crawl”.",
    downloadUrl: "/agents/yoink/SKILL.md",
  },
  {
    id: "cursor",
    label: "Cursor",
    shortLabel: "Cursor",
    installPath: ".cursor/rules/yoink.mdc",
    artifactFile: "cursor.mdc",
    artifactLabel: "cursor.mdc",
    installHint:
      "Save cursor.mdc to .cursor/rules/yoink.mdc inside your project. Cursor reads .mdc files from this directory automatically.",
    downloadUrl: "/agents/yoink/cursor.mdc",
  },
  {
    id: "windsurf",
    label: "Windsurf",
    shortLabel: "Windsurf",
    installPath: ".windsurfrules",
    artifactFile: ".windsurfrules",
    artifactLabel: ".windsurfrules",
    installHint:
      "Save .windsurfrules to the root of your project. Windsurf reads it as global rules for the workspace.",
    downloadUrl: "/agents/yoink/.windsurfrules",
  },
  {
    id: "codex",
    label: "Codex / generic",
    shortLabel: "Codex",
    installPath: "AGENTS.md",
    artifactFile: "AGENTS.md",
    artifactLabel: "AGENTS.md",
    installHint:
      "Drop AGENTS.md at the root of your repo. Works with Codex, OpenAI agents, and any assistant that reads the AGENTS.md convention.",
    downloadUrl: "/agents/yoink/AGENTS.md",
  },
];

export const DEFAULT_TOOL: Tool = "claude";

export function getToolMeta(id: Tool): ToolMeta {
  return TOOLS.find((t) => t.id === id) ?? TOOLS[0];
}
