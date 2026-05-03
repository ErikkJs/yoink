import * as React from "react";
import { useNavigate } from "react-router";
import * as Dialog from "@radix-ui/react-dialog";
import { search, highlightSegments, type SearchHit } from "../../lib/search";
import { cn } from "../../lib/utils";

interface SearchDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SearchDialog({ open, onOpenChange }: SearchDialogProps) {
  const [query, setQuery] = React.useState("");
  const [activeIndex, setActiveIndex] = React.useState(0);
  const navigate = useNavigate();
  const inputRef = React.useRef<HTMLInputElement>(null);
  const listRef = React.useRef<HTMLDivElement>(null);

  // Recompute hits whenever query changes. Cheap (≤25 docs).
  const hits: SearchHit[] = React.useMemo(() => {
    if (!query.trim()) return [];
    return search(query, 10);
  }, [query]);

  // Reset state when the dialog closes
  React.useEffect(() => {
    if (!open) {
      setQuery("");
      setActiveIndex(0);
    } else {
      // Defer focus so Radix has finished mounting
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [open]);

  // Reset active index when results change
  React.useEffect(() => {
    setActiveIndex(0);
  }, [hits.length]);

  // Scroll the active item into view as you arrow through
  React.useEffect(() => {
    if (!listRef.current) return;
    const el = listRef.current.querySelector<HTMLElement>(
      `[data-search-index="${activeIndex}"]`
    );
    if (el) el.scrollIntoView({ block: "nearest" });
  }, [activeIndex]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (hits.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, hits.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const hit = hits[activeIndex];
      if (hit) navigateTo(hit);
    }
  };

  const navigateTo = (hit: SearchHit) => {
    const target = `/docs/${hit.entry.slug}`;
    onOpenChange(false);
    navigate(target);
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <Dialog.Content
          onKeyDown={onKeyDown}
          className="fixed top-[14vh] left-1/2 -translate-x-1/2 z-50 w-[92vw] max-w-2xl overflow-hidden rounded-xl border border-border-strong bg-card shadow-2xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
        >
          <Dialog.Title className="sr-only">Search the docs</Dialog.Title>
          <Dialog.Description className="sr-only">
            Type to filter pages and headings. Use arrow keys to navigate, Enter
            to open.
          </Dialog.Description>

          {/* Input */}
          <div className="flex items-center gap-3 border-b border-border px-4 py-3.5">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              className="size-4 text-muted-foreground shrink-0"
            >
              <circle cx="11" cy="11" r="7" strokeWidth={1.7} />
              <path
                d="M21 21l-4.35-4.35"
                strokeWidth={1.7}
                strokeLinecap="round"
              />
            </svg>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search yoink docs…"
              className="flex-1 bg-transparent outline-none text-sm placeholder:text-muted-foreground/70"
              autoComplete="off"
              spellCheck={false}
            />
            <kbd className="font-mono text-[0.65rem] px-1.5 py-0.5 rounded border border-border bg-background/80 text-muted-foreground">
              esc
            </kbd>
          </div>

          {/* Results */}
          <div
            ref={listRef}
            className="max-h-[50vh] overflow-y-auto py-2"
          >
            {query.trim() && hits.length === 0 && (
              <div className="px-4 py-8 text-center">
                <p className="font-mono text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground/70 mb-1">
                  no matches
                </p>
                <p className="text-sm text-muted-foreground">
                  Nothing for{" "}
                  <code className="font-mono text-foreground">
                    "{query.slice(0, 30)}"
                  </code>
                </p>
              </div>
            )}

            {!query.trim() && (
              <div className="px-4 py-2 space-y-1">
                <p className="meta-pill mb-2 px-2">▸ start typing</p>
                <p className="px-2 text-sm text-muted-foreground">
                  Search across all pages, headings, and content. Try{" "}
                  <code className="font-mono text-foreground">checkpoint</code>,{" "}
                  <code className="font-mono text-foreground">rate limit</code>,
                  or{" "}
                  <code className="font-mono text-foreground">--include</code>.
                </p>
              </div>
            )}

            {hits.length > 0 && (
              <ul className="px-2 space-y-0.5">
                {hits.map((hit, i) => (
                  <li key={`${hit.entry.slug}-${i}`}>
                    <button
                      type="button"
                      data-search-index={i}
                      onClick={() => navigateTo(hit)}
                      onMouseMove={() => setActiveIndex(i)}
                      className={cn(
                        "w-full text-left rounded-md px-3 py-2.5 transition-colors flex flex-col gap-1",
                        i === activeIndex
                          ? "bg-lime/[0.08]"
                          : "hover:bg-muted/40"
                      )}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-baseline gap-2 min-w-0">
                          <span
                            className={cn(
                              "font-mono text-[0.62rem] uppercase tracking-[0.12em] shrink-0",
                              i === activeIndex
                                ? "text-lime"
                                : "text-muted-foreground/70"
                            )}
                          >
                            {hit.entry.section}
                          </span>
                          <span className="font-display font-semibold text-sm text-foreground truncate">
                            <Highlight text={hit.entry.title} query={query} />
                          </span>
                        </div>
                        <span
                          className={cn(
                            "font-mono text-[0.65rem] shrink-0",
                            i === activeIndex
                              ? "text-lime"
                              : "text-muted-foreground/50"
                          )}
                        >
                          ↵
                        </span>
                      </div>

                      <div className="text-[0.78rem] text-muted-foreground leading-snug pl-0">
                        {hit.match.type === "keyword" && (
                          <span>
                            <span className="text-lime/70">▸ matches</span>{" "}
                            <span className="font-mono text-foreground/85">
                              <Highlight text={hit.match.text} query={query} />
                            </span>
                            {hit.entry.description && (
                              <span className="text-muted-foreground/60">
                                {" · "}
                                {hit.entry.description.length > 60
                                  ? `${hit.entry.description.slice(0, 60)}…`
                                  : hit.entry.description}
                              </span>
                            )}
                          </span>
                        )}
                        {hit.match.type === "description" &&
                          hit.entry.description && (
                            <span className="line-clamp-2">
                              <Highlight
                                text={hit.entry.description}
                                query={query}
                              />
                            </span>
                          )}
                        {hit.match.type === "title" && hit.entry.description && (
                          <span className="line-clamp-1 text-muted-foreground/70">
                            {hit.entry.description}
                          </span>
                        )}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Footer with kbd hints */}
          <div className="flex items-center justify-between gap-3 border-t border-border px-4 py-2 bg-background/40 text-[0.7rem] text-muted-foreground">
            <div className="flex items-center gap-3 font-mono">
              <span className="flex items-center gap-1">
                <Kbd>↑</Kbd>
                <Kbd>↓</Kbd>
                <span className="ml-1">navigate</span>
              </span>
              <span className="flex items-center gap-1">
                <Kbd>↵</Kbd>
                <span className="ml-1">open</span>
              </span>
              <span className="flex items-center gap-1">
                <Kbd>esc</Kbd>
                <span className="ml-1">close</span>
              </span>
            </div>
            <span className="font-mono">{hits.length} results</span>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="font-mono text-[0.6rem] px-1.5 py-0.5 rounded border border-border bg-background/80 text-muted-foreground min-w-[1.25rem] text-center inline-flex items-center justify-center">
      {children}
    </kbd>
  );
}

function Highlight({ text, query }: { text: string; query: string }) {
  const segments = highlightSegments(text, query);
  return (
    <>
      {segments.map((s, i) =>
        s.match ? (
          <mark
            key={i}
            className="bg-lime/30 text-lime-bright rounded-sm px-0.5"
          >
            {s.text}
          </mark>
        ) : (
          <span key={i}>{s.text}</span>
        )
      )}
    </>
  );
}
