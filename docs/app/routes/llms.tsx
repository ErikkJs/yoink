import * as React from "react";
import type { Route } from "./+types/llms";
import { TopBar } from "../components/layout/TopBar";
import { useTool } from "../lib/llms/ToolContext";
import { TOOLS, getToolMeta, type Tool } from "../lib/llms/tools";
import { RECIPES } from "../lib/llms/recipes";
import {
  Dialog,
  DialogOverlay,
  DialogPortal,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "../components/ui/dialog";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { cn } from "../lib/utils";

export function meta(_: Route.MetaArgs) {
  return [
    { title: "For LLMs — yoink" },
    {
      name: "description",
      content:
        'Drop a yoink skill into Claude Code, Cursor, Windsurf, or Codex once. Say "scrape this" forever after.',
    },
  ];
}

export default function ForLLMsPage() {
  const { tool, setTool, hydrated } = useTool();
  const [activeRecipe, setActiveRecipe] = React.useState(RECIPES[0].id);
  const [copiedPrompt, setCopiedPrompt] = React.useState(false);
  const recipe = RECIPES.find((r) => r.id === activeRecipe) ?? RECIPES[0];
  const meta = getToolMeta(tool);
  const prompt = recipe.prompt(tool);

  const onCopyPrompt = async () => {
    try {
      await navigator.clipboard.writeText(prompt);
      setCopiedPrompt(true);
      setTimeout(() => setCopiedPrompt(false), 1500);
    } catch {}
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <TopBar />
      <main className="mx-auto w-full max-w-4xl px-6 py-10 lg:py-12">
        <div className="rounded-lg overflow-hidden border border-border-strong shadow-[0_24px_80px_-32px_rgba(0,0,0,0.8)]">
          {/* Titlebar */}
          <div className="flex items-center gap-2 px-4 py-2.5 bg-card/80 border-b border-border">
            <div className="flex gap-1.5">
              <span className="size-3 rounded-full bg-[#ff5f57]" />
              <span className="size-3 rounded-full bg-[#febc2e]" />
              <span className="size-3 rounded-full bg-[#28c840]" />
            </div>
            <span className="flex-1 text-center font-mono text-[0.7rem] text-muted-foreground">
              ~/yoink — bash — 80×24
            </span>
            <span className="w-16" />
          </div>

          {/* Terminal body */}
          <div className="bg-[#0a0f0a] font-mono text-[0.85rem] leading-[1.65] p-6 space-y-4">
            <Block>
              <Line prompt>yoink --help-ai</Line>
              <Comment># Yoink works with your AI assistant.</Comment>
              <Comment># Drop one file. Say "scrape X" forever.</Comment>
            </Block>

            <Block>
              <Line label>? which AI are you using?</Line>
              <div className="flex flex-wrap gap-1.5 ml-4">
                {TOOLS.map((t) => {
                  const active = t.id === tool;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setTool(t.id)}
                      className={cn(
                        "px-2.5 py-1 rounded text-[0.75rem] transition-colors",
                        hydrated && active
                          ? "text-lime bg-lime/10 border border-lime/40"
                          : "text-foreground/60 border border-foreground/15 hover:text-foreground/90 hover:border-foreground/30",
                      )}
                    >
                      {hydrated && active ? "❯ ●" : "  ○"} {t.shortLabel}
                    </button>
                  );
                })}
              </div>
            </Block>

            {/* ── 01 INSTALL ─────────────────────────────────── */}
            <Block>
              <Comment>─── 01 ─ install ──────────────────────────────────────────</Comment>
              <Line prompt>cat {meta.artifactFile}</Line>
              <SkillPreview tool={tool} />

              <div className="mt-3 ml-4">
                <Comment># save it to:</Comment>
                <Line prompt>echo "↓" &gt; {meta.installPath}</Line>
              </div>
            </Block>

            {/* ── 02 RECIPES ─────────────────────────────────── */}
            <Block>
              <Comment>─── 02 ─ recipes ──────────────────────────────────────────</Comment>
              <Line prompt>recipes ls</Line>
              <div className="flex flex-wrap gap-1.5 ml-4 mt-1">
                {RECIPES.map((r) => {
                  const active = r.id === activeRecipe;
                  return (
                    <button
                      key={r.id}
                      onClick={() => setActiveRecipe(r.id)}
                      className={cn(
                        "text-[0.75rem] px-2 py-0.5 rounded transition-colors",
                        active
                          ? "text-lime"
                          : "text-foreground/50 hover:text-foreground/80",
                      )}
                    >
                      {active ? "● " : "○ "}
                      {r.id}
                    </button>
                  );
                })}
              </div>
              <Line prompt>recipes show {recipe.id}</Line>
              <div className="ml-4 mt-2 rounded border border-foreground/15 bg-background/60">
                <div className="px-3 py-2 border-b border-foreground/10 flex items-center justify-between text-[0.7rem]">
                  <span className="text-foreground/50">prompt</span>
                  <button
                    onClick={onCopyPrompt}
                    className={cn(
                      "px-2 py-0.5 rounded transition-colors",
                      copiedPrompt
                        ? "text-lime bg-lime/10"
                        : "text-foreground/50 hover:text-foreground/90",
                    )}
                  >
                    {copiedPrompt ? "✓ copied" : "[ copy ]"}
                  </button>
                </div>
                <pre className="px-3 py-3 text-[0.72rem] leading-relaxed text-foreground/85 whitespace-pre-wrap break-words max-h-72 overflow-auto">
                  {prompt}
                </pre>
              </div>
            </Block>

            <Block>
              <Comment>─── 03 ─ docs ─ feed yoink to your AI ────────────────────</Comment>
              <Line prompt>cat /llms-full.txt | pbcopy</Line>
              <div className="ml-4 mt-1 flex flex-wrap gap-2 text-[0.75rem]">
                <a
                  href="/llms.txt"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-lime hover:underline"
                >
                  /llms.txt
                </a>
                <span className="text-foreground/30">·</span>
                <a
                  href="/llms-full.txt"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-lime hover:underline"
                >
                  /llms-full.txt
                </a>
                <span className="text-foreground/30">·</span>
                <span className="text-foreground/50">
                  or click <span className="text-foreground/80">copy as markdown</span> on any docs page
                </span>
              </div>
            </Block>

            <Block>
              <Line prompt blink>
                _
              </Line>
            </Block>
          </div>
        </div>
      </main>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────
// Skill preview + viewer
// ──────────────────────────────────────────────────────────────

const SKILL_CACHE: Partial<Record<Tool, string>> = {};

function useSkillContent(tool: Tool) {
  const meta = getToolMeta(tool);
  const [content, setContent] = React.useState<string | null>(SKILL_CACHE[tool] ?? null);
  const [loading, setLoading] = React.useState(SKILL_CACHE[tool] === undefined);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (SKILL_CACHE[tool] !== undefined) {
      setContent(SKILL_CACHE[tool]!);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    fetch(meta.downloadUrl)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.text();
      })
      .then((text) => {
        SKILL_CACHE[tool] = text;
        setContent(text);
        setLoading(false);
      })
      .catch((e) => {
        setError(String(e));
        setLoading(false);
      });
  }, [tool, meta.downloadUrl]);

  return { content, loading, error };
}

function SkillPreview({ tool }: { tool: Tool }) {
  const meta = getToolMeta(tool);
  const { content, loading, error } = useSkillContent(tool);
  const [copiedContents, setCopiedContents] = React.useState(false);
  const [copiedAi, setCopiedAi] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  const onCopyContents = async () => {
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      setCopiedContents(true);
      setTimeout(() => setCopiedContents(false), 1500);
    } catch {}
  };

  const onCopyAiPrompt = async () => {
    if (!content) return;
    try {
      await navigator.clipboard.writeText(buildInstallPrompt(tool, content));
      setCopiedAi(true);
      setTimeout(() => setCopiedAi(false), 2000);
    } catch {}
  };

  // Show the first ~8 lines as a teaser. For .mdc / .windsurfrules / AGENTS.md
  // the body is similar; the frontmatter differs.
  const teaser = React.useMemo(() => {
    if (!content) return "";
    const lines = content.split("\n");
    return lines.slice(0, 8).join("\n");
  }, [content]);

  return (
    <div className="ml-4 mt-1">
      {/* File card — click anywhere to open the viewer */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="group w-full text-left rounded border border-foreground/15 bg-background/60 overflow-hidden hover:border-lime/40 transition-colors"
        aria-label={`View ${meta.artifactFile}`}
      >
        <div className="flex items-center gap-2 px-3 py-1.5 border-b border-foreground/10 bg-foreground/[0.03]">
          <span className="text-[0.65rem] text-foreground/60 font-medium">
            <span className="text-foreground/40">📄</span> {meta.artifactFile}
          </span>
          <span className="text-[0.6rem] text-foreground/40">·</span>
          <span className="text-[0.6rem] text-foreground/40 truncate">for {meta.label}</span>
          <span className="ml-auto text-[0.6rem] text-foreground/40 group-hover:text-lime transition-colors">
            click to view ↗
          </span>
        </div>
        <pre className="px-3 py-2 text-[0.7rem] text-foreground/70 leading-relaxed overflow-hidden whitespace-pre-wrap max-h-[7.5rem] relative">
          {loading ? "// loading...\n" : error ? `// error: ${error}\n` : teaser}
          <span className="absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-background/95 to-transparent pointer-events-none" />
        </pre>
      </button>

      {/* Primary: AI-driven install (one-paste, no thinking required) */}
      <div className="mt-3">
        <div className="text-foreground/35 italic text-[0.75rem] mb-1.5">
          # easy: let {meta.label} install it for you
        </div>
        <button
          onClick={onCopyAiPrompt}
          disabled={!content}
          className={cn(
            "w-full sm:w-auto inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-md text-[0.8rem] font-medium border transition-colors",
            copiedAi
              ? "text-lime bg-lime/10 border-lime/40"
              : content
                ? "text-background bg-lime border-lime hover:bg-lime-bright shadow-[0_0_0_1px_hsl(var(--lime)/0.6),0_6px_16px_-6px_hsl(var(--lime)/0.5)]"
                : "text-foreground/40 border-foreground/15 cursor-not-allowed",
          )}
        >
          {copiedAi ? (
            <>✓ install prompt copied — paste into {meta.label}</>
          ) : (
            <>🤖 copy install prompt for {meta.shortLabel}</>
          )}
        </button>
        {copiedAi && (
          <p className="mt-1.5 text-[0.7rem] text-foreground/50">
            Open {meta.label}, paste it as a new message. It'll create {meta.installPath} for you.
          </p>
        )}
      </div>

      {/* Secondary: manual install options */}
      <div className="mt-4">
        <div className="text-foreground/35 italic text-[0.75rem] mb-1.5">
          # manual: copy &amp; save it yourself
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={onCopyContents}
            disabled={!content}
            className={cn(
              "text-[0.7rem] px-2 py-0.5 rounded transition-colors border",
              copiedContents
                ? "text-lime bg-lime/10 border-lime/40"
                : content
                  ? "text-foreground/85 border-foreground/25 hover:text-foreground hover:border-foreground/40"
                  : "text-foreground/40 border-foreground/15 cursor-not-allowed",
            )}
          >
            {copiedContents ? "✓ copied" : "[ 📋 copy contents ]"}
          </button>
          <button
            onClick={() => setOpen(true)}
            className="text-[0.7rem] px-2 py-0.5 rounded text-foreground/60 border border-foreground/20 hover:text-foreground/90 hover:border-foreground/40 transition-colors"
          >
            [ 👁 view ]
          </button>
          <a
            href={meta.downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[0.7rem] px-2 py-0.5 rounded text-foreground/60 border border-foreground/20 hover:text-foreground/90 hover:border-foreground/40 transition-colors"
          >
            [ 🌐 raw ↗ ]
          </a>
          <a
            href={meta.downloadUrl}
            download={meta.artifactFile}
            className="text-[0.7rem] px-2 py-0.5 rounded text-foreground/40 hover:text-foreground/70 transition-colors"
          >
            [ ⬇ download ]
          </a>
        </div>
      </div>

      <SkillViewer
        open={open}
        onOpenChange={setOpen}
        tool={tool}
        content={content}
        loading={loading}
        error={error}
      />
    </div>
  );
}

function buildInstallPrompt(tool: Tool, content: string): string {
  const meta = getToolMeta(tool);
  switch (tool) {
    case "claude":
      return `Please install the yoink skill for Claude Code.

This will teach you how to use yoink (a Python web crawler) whenever I ask you to scrape, crawl, mirror, or build a training dataset from a website.

Steps:
1. Create the directory if it doesn't exist: \`mkdir -p ~/.claude/skills/yoink\`
2. Save the content between <file>...</file> below to \`${meta.installPath}\`
3. Confirm the file is in place: \`ls -la ~/.claude/skills/yoink/\`

<file path="${meta.installPath}">
${content}
</file>

Once it's saved, the skill activates automatically the next time I say something like "scrape this site" or "mirror these docs."`;

    case "cursor":
      return `Please install the yoink rules for this Cursor project.

This will teach you how to use yoink (a Python web crawler) when I ask you to scrape or crawl websites.

Steps:
1. Create the directory if it doesn't exist: \`mkdir -p .cursor/rules\`
2. Save the content between <file>...</file> below to \`${meta.installPath}\`
3. Confirm the file is in place

<file path="${meta.installPath}">
${content}
</file>

Cursor will pick up this rules file automatically for any matching context.`;

    case "windsurf":
      return `Please create or update \`.windsurfrules\` at this project's root with the yoink instructions below.

This will teach you how to use yoink (a Python web crawler) whenever I ask you to scrape, crawl, or mirror websites.

If \`.windsurfrules\` already exists, append the content as a new section. Otherwise create it from scratch.

<file path="${meta.installPath}">
${content}
</file>`;

    case "codex":
      return `Please install yoink instructions into this repo's \`AGENTS.md\` file.

This teaches any agent working in this codebase how to use yoink (a Python web crawler) for crawling and scraping tasks.

If \`AGENTS.md\` already exists at the project root, append the content below as a new section. Otherwise create it from scratch.

<file path="${meta.installPath}">
${content}
</file>`;
  }
}

function SkillViewer({
  open,
  onOpenChange,
  tool,
  content,
  loading,
  error,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tool: Tool;
  content: string | null;
  loading: boolean;
  error: string | null;
}) {
  const meta = getToolMeta(tool);
  const [copied, setCopied] = React.useState(false);

  const onCopy = async () => {
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {}
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogPortal>
        <DialogOverlay />
        <DialogPrimitive.Content
          className={cn(
            "fixed left-[50%] top-[50%] z-50 flex flex-col w-[calc(100%-2rem)] max-w-3xl translate-x-[-50%] translate-y-[-50%]",
            "h-[85vh] max-h-[85vh] rounded-lg border border-border-strong overflow-hidden",
            "shadow-[0_24px_80px_-32px_rgba(0,0,0,0.9)] duration-200",
            "data-[state=open]:animate-in data-[state=closed]:animate-out",
            "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
            "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
          )}
        >
          {/* Terminal-window titlebar */}
          <div className="flex items-center gap-2 px-4 py-2.5 bg-card border-b border-border shrink-0">
            <div className="flex gap-1.5">
              <DialogClose
                className="size-3 rounded-full bg-[#ff5f57] hover:opacity-80"
                aria-label="Close"
              />
              <span className="size-3 rounded-full bg-[#febc2e]" />
              <span className="size-3 rounded-full bg-[#28c840]" />
            </div>
            <DialogTitle className="flex-1 text-center font-mono text-[0.7rem] text-muted-foreground font-normal">
              {meta.artifactFile} — {meta.label}
            </DialogTitle>
            <button
              onClick={onCopy}
              disabled={!content}
              className={cn(
                "inline-flex items-center gap-1.5 text-[0.7rem] px-2.5 py-1 rounded border transition-colors",
                copied
                  ? "text-lime bg-lime/10 border-lime/40"
                  : content
                    ? "text-foreground/80 bg-card border-border hover:border-border-strong hover:text-foreground"
                    : "text-foreground/40 border-foreground/15 cursor-not-allowed",
              )}
            >
              {copied ? "✓ copied" : "📋 copy all"}
            </button>
          </div>

          {/* Body */}
          <div className="bg-[#0a0f0a] flex-1 overflow-auto min-h-0">
            <DialogDescription className="sr-only">
              Contents of {meta.artifactFile} — copy or read to install yoink into {meta.label}.
            </DialogDescription>
            {loading ? (
              <div className="p-6 font-mono text-sm text-foreground/60">
                loading {meta.artifactFile}...
              </div>
            ) : error ? (
              <div className="p-6 font-mono text-sm text-destructive">error: {error}</div>
            ) : (
              <pre className="text-[0.78rem] font-mono leading-[1.7] whitespace-pre overflow-x-auto">
                {content?.split("\n").map((line, i) => (
                  <div
                    key={i}
                    className="flex hover:bg-foreground/[0.03] px-5 first:pt-4 last:pb-4"
                  >
                    <span className="select-none text-foreground/25 w-10 shrink-0 text-right pr-3 tabular-nums">
                      {i + 1}
                    </span>
                    <span className={cn("flex-1", lineClass(line))}>{line || " "}</span>
                  </div>
                ))}
              </pre>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2.5 bg-card border-t border-border shrink-0 flex items-center justify-between gap-3 flex-wrap">
            <span className="font-mono text-[0.7rem] text-muted-foreground truncate">
              save to: <span className="text-foreground/80">{meta.installPath}</span>
            </span>
            <div className="flex items-center gap-2 shrink-0">
              <a
                href={meta.downloadUrl}
                download={meta.artifactFile}
                className="text-[0.7rem] px-2.5 py-1 rounded text-muted-foreground hover:text-foreground border border-border hover:border-border-strong"
              >
                ⬇ download
              </a>
              <DialogClose className="text-[0.7rem] px-2.5 py-1 rounded text-muted-foreground hover:text-foreground border border-border hover:border-border-strong">
                close
              </DialogClose>
            </div>
          </div>
        </DialogPrimitive.Content>
      </DialogPortal>
    </Dialog>
  );
}

function lineClass(line: string): string {
  if (line.startsWith("---")) return "text-cyan/70";
  if (line.startsWith("# ")) return "text-lime font-semibold";
  if (line.startsWith("## ")) return "text-lime/80";
  if (line.startsWith("### ")) return "text-lime/60";
  if (line.startsWith("> ")) return "text-amber/80 italic";
  if (line.match(/^\s*-\s/)) return "text-foreground/80";
  if (line.match(/^\s*\d+\.\s/)) return "text-foreground/80";
  if (line.startsWith("```")) return "text-magenta/70";
  if (line.match(/^[a-z_]+:\s/i)) return "text-cyan/70";
  return "text-foreground/85";
}

// ──────────────────────────────────────────────────────────────
// Terminal primitives
// ──────────────────────────────────────────────────────────────

function Block({ children }: { children: React.ReactNode }) {
  return <div className="space-y-1">{children}</div>;
}

function Line({
  children,
  prompt,
  label,
  blink,
}: {
  children: React.ReactNode;
  prompt?: boolean;
  label?: boolean;
  blink?: boolean;
}) {
  return (
    <div className="flex items-start gap-2">
      {prompt && <span className="text-lime select-none">$</span>}
      {label && <span className="text-amber select-none">?</span>}
      <span
        className={cn(
          "text-foreground/90",
          blink && "animate-pulse text-foreground/40",
        )}
      >
        {children}
      </span>
    </div>
  );
}

function Comment({ children }: { children: React.ReactNode }) {
  return <div className="text-foreground/35 italic">{children}</div>;
}
