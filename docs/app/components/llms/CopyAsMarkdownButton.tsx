import * as React from "react";
import { cn } from "../../lib/utils";

interface CopyAsMarkdownButtonProps {
  slug: string;
  className?: string;
}

export function CopyAsMarkdownButton({ slug, className }: CopyAsMarkdownButtonProps) {
  const [state, setState] = React.useState<"idle" | "copying" | "copied" | "error">("idle");

  const onClick = async () => {
    setState("copying");
    try {
      const res = await fetch(`/docs.md/${slug}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const text = await res.text();
      await navigator.clipboard.writeText(text);
      setState("copied");
      setTimeout(() => setState("idle"), 1500);
    } catch {
      setState("error");
      setTimeout(() => setState("idle"), 2000);
    }
  };

  let label: string;
  switch (state) {
    case "copying":
      label = "copying...";
      break;
    case "copied":
      label = "copied for LLM ✓";
      break;
    case "error":
      label = "copy failed";
      break;
    default:
      label = "copy as markdown";
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1 hover:text-lime transition-colors",
        state === "copied" && "text-lime",
        state === "error" && "text-destructive",
        className,
      )}
      aria-label="Copy this page as markdown for pasting into an AI assistant"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="size-3">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
        />
      </svg>
      {label}
    </button>
  );
}
