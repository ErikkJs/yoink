import { DiagramFrame } from "./DiagramFrame";

/**
 * How `create_fetcher()` picks between the HTTP and Playwright paths.
 * Branches on `render_js` AND on whether `playwright` is importable.
 */
export function FetcherDispatch() {
  return (
    <DiagramFrame
      label="fetcher / dispatch"
      source="fetcher_factory.py"
      caption="render_js=True with Playwright missing → emits UserWarning, falls back to HTTP."
    >
      <div className="@container flex flex-col gap-3">
        {/* Entry */}
        <div className="self-center flex items-center gap-2">
          <span className="meta-pill text-foreground">create_fetcher(config)</span>
        </div>

        {/* Branch line */}
        <div className="relative h-6 flex justify-center">
          <div className="absolute top-0 left-1/4 right-1/4 h-3 border-t border-l border-r border-border-strong rounded-t-md" />
          <div className="absolute top-3 left-1/4 h-3 w-px bg-border-strong" />
          <div className="absolute top-3 right-1/4 h-3 w-px bg-border-strong" />
        </div>

        {/* Two paths */}
        <div className="grid grid-cols-1 @xl:grid-cols-2 gap-3">
          {/* HTTP path */}
          <div className="rounded-lg border border-cyan/40 bg-cyan/[0.04] overflow-hidden">
            <div className="px-4 py-2 border-b border-cyan/20 flex items-center justify-between">
              <span className="meta-pill text-cyan">HTTP path</span>
              <code className="font-mono text-[0.65rem] text-muted-foreground">
                render_js=False
              </code>
            </div>
            <div className="p-4 space-y-2">
              <p className="font-mono text-[0.82rem] text-foreground">Fetcher</p>
              <ul className="space-y-1 text-[0.78rem] text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-cyan">▸</span>
                  <span>aiohttp ClientSession</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-cyan">▸</span>
                  <span>3 attempts, exponential backoff</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-cyan">▸</span>
                  <span>fast, lean — the default</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Playwright path */}
          <div className="rounded-lg border border-magenta/40 bg-magenta/[0.04] overflow-hidden">
            <div className="px-4 py-2 border-b border-magenta/20 flex items-center justify-between">
              <span className="meta-pill text-magenta">browser path</span>
              <code className="font-mono text-[0.65rem] text-muted-foreground">
                render_js=True
              </code>
            </div>
            <div className="p-4 space-y-2">
              <p className="font-mono text-[0.82rem] text-foreground">PlaywrightFetcher</p>
              <ul className="space-y-1 text-[0.78rem] text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-magenta">▸</span>
                  <span>launch browser (chromium / firefox / webkit)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-magenta">▸</span>
                  <span>borrow context from pool</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-magenta">▸</span>
                  <span>page.goto(url) + wait_strategy</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-magenta">▸</span>
                  <span>optional wait_for_selector</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-magenta">▸</span>
                  <span>page.content() → html</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-magenta">▸</span>
                  <span>release context back to pool</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Fallback note */}
        <div className="mt-2 px-3 py-2 rounded-md bg-amber/[0.07] border border-amber/30 flex items-start gap-2">
          <span className="font-mono text-amber text-sm shrink-0">!</span>
          <p className="text-[0.8rem] text-foreground/85">
            <span className="font-mono text-amber">render_js=True + playwright missing</span>{" "}
            → emits <code className="font-mono text-amber/90">UserWarning</code>{" "}
            and silently falls back to the HTTP path.
          </p>
        </div>
      </div>
    </DiagramFrame>
  );
}
