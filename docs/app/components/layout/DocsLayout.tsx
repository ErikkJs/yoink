import { useEffect, useState } from "react";
import { Outlet } from "react-router";
import { TopBar } from "./TopBar";
import { DocsSidebar } from "./Sidebar";
import { cn } from "../../lib/utils";

export function DocsLayout() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  // Close mobile nav when crossing breakpoint
  useEffect(() => {
    const mq = window.matchMedia("(min-width: 768px)");
    const onChange = (e: MediaQueryListEvent | MediaQueryList) => {
      if (e.matches) setMobileNavOpen(false);
    };
    onChange(mq);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <TopBar onMenuClick={() => setMobileNavOpen((v) => !v)} />

      <div className="flex flex-1">
        {/* Desktop sidebar */}
        <aside className="hidden md:block w-64 lg:w-72 border-r border-border shrink-0 sticky top-14 self-start h-[calc(100vh-3.5rem)] overflow-y-auto bg-card/30">
          <DocsSidebar />
        </aside>

        {/* Mobile drawer */}
        {mobileNavOpen && (
          <>
            <div
              className="md:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
              onClick={() => setMobileNavOpen(false)}
            />
            <aside
              className={cn(
                "md:hidden fixed top-14 left-0 bottom-0 w-72 bg-card border-r border-border z-50 overflow-y-auto",
                "animate-in slide-in-from-left duration-200"
              )}
            >
              <DocsSidebar onNavigate={() => setMobileNavOpen(false)} />
            </aside>
          </>
        )}

        {/* Main content */}
        <main className="flex-1 min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
