import { useEffect, useState } from "react";
import { cn } from "../../lib/utils";

export interface TocEntry {
  id: string;
  title: string;
  depth: number;
}

interface TableOfContentsProps {
  entries: TocEntry[];
}

export function TableOfContents({ entries }: TableOfContentsProps) {
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (entries.length === 0) return;

    const observer = new IntersectionObserver(
      (observed) => {
        const visible = observed
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length > 0) {
          setActive(visible[0].target.id);
        }
      },
      {
        rootMargin: "-80px 0px -70% 0px",
        threshold: [0, 1],
      }
    );

    entries.forEach((entry) => {
      const el = document.getElementById(entry.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [entries]);

  if (entries.length === 0) return null;

  return (
    <nav className="space-y-3 text-sm">
      <p className="meta-pill">▸ on this page</p>
      <ul className="space-y-1 border-l border-border">
        {entries.map((entry) => (
          <li key={entry.id} style={{ paddingLeft: `${(entry.depth - 1) * 0.75}rem` }}>
            <a
              href={`#${entry.id}`}
              className={cn(
                "block -ml-px pl-3 border-l-2 transition-all leading-snug py-1 text-[0.825rem]",
                active === entry.id
                  ? "border-lime text-lime font-medium"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              {entry.title}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
