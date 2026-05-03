import { Link, useLocation } from "react-router";
import { cn } from "../../lib/utils";
import { docsNav } from "../../data/nav";

interface SidebarProps {
  onNavigate?: () => void;
}

export function DocsSidebar({ onNavigate }: SidebarProps) {
  const location = useLocation();
  const currentSlug = location.pathname.replace(/^\/docs\/?/, "");

  return (
    <div className="flex flex-col h-full">
      <nav className="flex-1 px-4 py-6 space-y-7">
        {docsNav.map((section, sectionIdx) => (
          <div key={section.title} className="space-y-2">
            <p className="px-2 meta-pill flex items-center gap-2">
              <span className="font-mono text-lime/70">
                {String(sectionIdx + 1).padStart(2, "0")}
              </span>
              <span>{section.title}</span>
            </p>
            <ul className="space-y-px">
              {section.items.map((item) => {
                const active = currentSlug === item.slug;
                return (
                  <li key={item.slug}>
                    <Link
                      to={`/docs/${item.slug}`}
                      onClick={onNavigate}
                      className={cn(
                        "group relative flex items-center gap-2.5 rounded-md pl-4 pr-2 py-1.5 text-[0.875rem] transition-all",
                        active
                          ? "text-foreground bg-lime/[0.06]"
                          : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
                      )}
                    >
                      {/* Active indicator bar */}
                      <span
                        className={cn(
                          "absolute left-0 top-1.5 bottom-1.5 w-[2px] rounded-full transition-all",
                          active ? "bg-lime" : "bg-transparent"
                        )}
                      />
                      {item.title}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer stats */}
      <div className="px-4 py-4 border-t border-border space-y-1.5">
        <div className="flex items-center justify-between font-mono text-[0.65rem] text-muted-foreground/80">
          <span>v0.1.0</span>
          <span className="flex items-center gap-1.5">
            <span className="live-dot" />
            134 tests
          </span>
        </div>
        <div className="flex items-center justify-between font-mono text-[0.65rem] text-muted-foreground/60">
          <span>3,164 LOC</span>
          <span>MIT</span>
        </div>
      </div>
    </div>
  );
}
