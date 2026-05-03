import { Link } from "react-router";
import type { NavItem } from "../../data/nav";

interface PrevNextProps {
  prev: NavItem | null;
  next: NavItem | null;
}

export function PrevNext({ prev, next }: PrevNextProps) {
  if (!prev && !next) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-16 pt-8 border-t border-border">
      {prev ? (
        <Link
          to={`/docs/${prev.slug}`}
          className="group flex flex-col gap-1.5 rounded-lg border border-border bg-card/40 hover:bg-card hover:border-lime/30 px-4 py-3 transition-all"
        >
          <span className="meta-pill flex items-center gap-1.5 text-muted-foreground group-hover:text-lime transition-colors">
            <span className="font-mono">←</span>
            Previous
          </span>
          <span className="font-display font-semibold text-foreground group-hover:text-lime transition-colors">
            {prev.title}
          </span>
        </Link>
      ) : (
        <div />
      )}
      {next ? (
        <Link
          to={`/docs/${next.slug}`}
          className="group flex flex-col gap-1.5 rounded-lg border border-border bg-card/40 hover:bg-card hover:border-lime/30 px-4 py-3 transition-all text-right sm:items-end"
        >
          <span className="meta-pill flex items-center gap-1.5 text-muted-foreground group-hover:text-lime transition-colors justify-end">
            Next
            <span className="font-mono">→</span>
          </span>
          <span className="font-display font-semibold text-foreground group-hover:text-lime transition-colors">
            {next.title}
          </span>
        </Link>
      ) : null}
    </div>
  );
}
