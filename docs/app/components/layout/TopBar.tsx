import * as React from "react";
import { Link } from "react-router";
import { Button } from "../ui/button";
import { cn } from "../../lib/utils";
import { SearchDialog } from "./SearchDialog";

interface TopBarProps {
  onMenuClick?: () => void;
  className?: string;
}

export function TopBar({ onMenuClick, className }: TopBarProps) {
  const [searchOpen, setSearchOpen] = React.useState(false);

  // Cmd+K / Ctrl+K — global open
  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen((v) => !v);
      } else if (e.key === "/" && !isTypingTarget(e.target)) {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-30 h-14 border-b border-border bg-background/85 backdrop-blur-xl",
        className
      )}
    >
      <div className="flex h-full items-center justify-between px-4 md:px-6">
        {/* Left: brand */}
        <div className="flex items-center gap-3">
          {onMenuClick && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={onMenuClick}
              aria-label="Toggle navigation"
              className="md:hidden"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeWidth={1.8}
                  d="M4 7h16M4 12h16M4 17h16"
                />
              </svg>
            </Button>
          )}

          <Link to="/" className="flex items-baseline gap-2.5 group">
            <span className="font-display text-xl font-bold tracking-tight italic group-hover:text-lime transition-colors">
              yoink
            </span>
            <span className="hidden sm:inline-flex meta-pill">
              <span className="live-dot" />
              v0.1.0
            </span>
          </Link>
        </div>

        {/* Center: nav (desktop) */}
        <nav className="hidden md:flex items-center gap-0.5 absolute left-1/2 -translate-x-1/2">
          <NavLink to="/docs/introduction">Docs</NavLink>
          <NavLink to="/docs/cli/crawl">CLI</NavLink>
          <NavLink to="/docs/api/crawler">API</NavLink>
          <NavLink to="/docs/examples/basic">Examples</NavLink>
          <NavLink to="/llms">
            <span className="inline-flex items-center gap-1.5">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="size-3.5">
                <path
                  strokeWidth={1.6}
                  strokeLinecap="round"
                  d="M12 3v6m0 6v6m-9-9h6m6 0h6"
                />
                <path
                  strokeWidth={1.3}
                  strokeLinecap="round"
                  d="M6.5 6.5l3 3m5 5l3 3m0-11l-3 3m-5 5l-3 3"
                  opacity={0.55}
                />
              </svg>
              For LLMs
            </span>
          </NavLink>
        </nav>

        {/* Right: actions */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setSearchOpen(true)}
            className="hidden md:inline-flex items-center gap-2 h-8 pl-2.5 pr-1.5 rounded-md text-xs text-muted-foreground border border-border bg-card/40 hover:bg-card hover:border-border-strong hover:text-foreground transition-colors mr-1 group"
            aria-label="Search the docs"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="size-3.5">
              <circle cx="11" cy="11" r="7" strokeWidth={1.7} />
              <path d="M21 21l-4.35-4.35" strokeWidth={1.7} strokeLinecap="round" />
            </svg>
            <span>Search the docs</span>
            <kbd className="ml-3 font-mono text-[0.65rem] px-1.5 py-0.5 rounded border border-border bg-background/80 text-muted-foreground group-hover:border-border-strong">⌘K</kbd>
          </button>

          {/* Mobile search icon */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setSearchOpen(true)}
            className="md:hidden"
            aria-label="Search"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="size-[18px]">
              <circle cx="11" cy="11" r="7" strokeWidth={1.7} />
              <path d="M21 21l-4.35-4.35" strokeWidth={1.7} strokeLinecap="round" />
            </svg>
          </Button>

          <Button variant="ghost" size="icon-sm" asChild>
            <a
              href="https://github.com/ErikkJs/yoink"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="size-[18px]">
                <path
                  fillRule="evenodd"
                  d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  clipRule="evenodd"
                />
              </svg>
            </a>
          </Button>
          <Button variant="lime" size="sm" asChild className="hidden sm:inline-flex">
            <Link to="/docs/quickstart">
              Get started
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="size-3.5 ml-0.5">
                <path strokeLinecap="round" strokeWidth={2} d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </Link>
          </Button>
        </div>
      </div>

      <SearchDialog open={searchOpen} onOpenChange={setSearchOpen} />
    </header>
  );
}

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      className="px-3 py-1.5 text-sm text-muted-foreground rounded-md hover:text-foreground hover:bg-muted/50 transition-colors"
    >
      {children}
    </Link>
  );
}

function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  return (
    tag === "INPUT" ||
    tag === "TEXTAREA" ||
    tag === "SELECT" ||
    target.isContentEditable
  );
}
