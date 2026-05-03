import { DiagramFrame } from "./DiagramFrame";

/**
 * EventBridge → Lambda → yoink → S3, with a resume loop.
 * Visual shows compute on top and persistent state on bottom, joined
 * by the read/write data path.
 */
export function LambdaArchitecture() {
  return (
    <DiagramFrame
      label="lambda + s3 / topology"
      source="examples/checkpoint_resume.py"
      caption="14-min budget per invocation · S3 stores progress · scheduled re-invocations resume until done."
    >
      <div className="@container space-y-3">
        {/* Top row: EventBridge → Lambda → Crawler — switches to horizontal
            once the diagram itself has at least 36rem of room. */}
        <div className="grid grid-cols-1 @xl:grid-cols-[1fr_auto_1fr_auto_1fr] gap-3 @xl:gap-2 items-stretch">
          {/* EventBridge */}
          <div className="rounded-lg border border-amber/40 bg-amber/[0.05] p-3 flex flex-col justify-between min-h-[88px]">
            <div className="flex items-center justify-between mb-1">
              <span className="meta-pill text-amber">trigger</span>
              <span className="font-mono text-[0.6rem] text-muted-foreground/70">aws</span>
            </div>
            <p className="font-display font-semibold leading-tight">EventBridge</p>
            <p className="font-mono text-[0.7rem] text-muted-foreground">
              rate(14 minutes)
            </p>
          </div>

          <Arrow label="invoke" />

          {/* Lambda */}
          <div className="rounded-lg border border-lime/50 bg-lime/[0.06] p-3 flex flex-col justify-between min-h-[88px]">
            <div className="flex items-center justify-between mb-1">
              <span className="meta-pill text-lime">compute</span>
              <span className="font-mono text-[0.6rem] text-lime/80">15-min cap</span>
            </div>
            <p className="font-display font-semibold leading-tight">Lambda function</p>
            <p className="font-mono text-[0.7rem] text-muted-foreground">
              python3.11 · 1024 MB
            </p>
          </div>

          <Arrow label="run" />

          {/* yoink Crawler */}
          <div className="rounded-lg border border-cyan/40 bg-cyan/[0.05] p-3 flex flex-col justify-between min-h-[88px]">
            <div className="flex items-center justify-between mb-1">
              <span className="meta-pill text-cyan">app</span>
              <span className="font-mono text-[0.6rem] text-muted-foreground/70">
                yoink
              </span>
            </div>
            <p className="font-display font-semibold leading-tight">Crawler</p>
            <p className="font-mono text-[0.7rem] text-muted-foreground">
              CheckpointManager.from_uri(s3://…)
            </p>
          </div>
        </div>

        {/* Vertical down arrows from Lambda + Crawler to S3 */}
        <div className="hidden @xl:flex items-center justify-end pr-[18%] gap-2 text-muted-foreground/60">
          <span className="font-mono text-xs">read state ↑ · write progress ↓</span>
          <span className="font-mono text-base">↕</span>
        </div>
        <div className="@xl:hidden flex items-center justify-center text-muted-foreground/60 font-mono">
          ↕ read/write
        </div>

        {/* Bottom row: S3 (persistent) */}
        <div className="rounded-lg border border-magenta/40 bg-magenta/[0.05] p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="meta-pill text-magenta">persistent state</span>
            <span className="font-mono text-[0.6rem] text-muted-foreground/70">
              s3://my-crawl-bucket/checkpoints/example.jsonl
            </span>
          </div>
          <div className="grid grid-cols-3 gap-px bg-border-strong/40 rounded overflow-hidden">
            <Cell label="metadata" hint="run header" />
            <Cell label="page × N" hint="streamed appends" />
            <Cell label="state × M" hint="every flush_interval" />
          </div>
        </div>

        {/* Resume loop annotation */}
        <div className="rounded-lg border border-border bg-background/40 p-3 flex items-start gap-3">
          <span className="font-mono text-lime text-base shrink-0 leading-none mt-0.5">↻</span>
          <div className="text-[0.82rem] text-foreground/85 leading-relaxed">
            <span className="font-mono text-lime">resume=True</span>: when EventBridge
            fires the next invocation, the Crawler reads the checkpoint object,
            restores{" "}
            <span className="font-mono text-foreground">visited / queue / filtered</span>
            , and continues exactly where the previous run stopped. Repeats until
            the crawl finishes or you disable the rule.
          </div>
        </div>
      </div>
    </DiagramFrame>
  );
}

function Arrow({ label }: { label?: string }) {
  return (
    <div className="hidden @xl:flex flex-col items-center justify-center min-w-[40px]">
      <span className="font-mono text-[0.6rem] text-muted-foreground/70 mb-0.5">
        {label}
      </span>
      <span className="text-muted-foreground/40 font-mono text-lg leading-none">→</span>
    </div>
  );
}

function Cell({ label, hint }: { label: string; hint: string }) {
  return (
    <div className="bg-background px-3 py-2 text-center">
      <p className="font-mono text-[0.78rem] text-foreground">{label}</p>
      <p className="font-mono text-[0.65rem] text-muted-foreground/70 mt-0.5">{hint}</p>
    </div>
  );
}
