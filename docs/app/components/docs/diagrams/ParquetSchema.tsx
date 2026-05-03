import { DiagramFrame } from "./DiagramFrame";

interface SchemaColumn {
  name: string;
  type: string;
  note?: string;
  highlight?: boolean;
}

const defaultColumns: SchemaColumn[] = [
  { name: "url", type: "string" },
  { name: "title", type: "string?", note: "nullable" },
  { name: "text", type: "string?", note: "nullable" },
  { name: "crawled_at", type: "string", note: "ISO 8601 timestamp" },
  { name: "status_code", type: "int64" },
  { name: "depth", type: "int64" },
  { name: "num_links", type: "int64", note: "links list → count only", highlight: true },
  { name: "metadata", type: "string", note: "JSON-encoded dict", highlight: true },
];

interface ParquetSchemaProps {
  /** Override columns if needed; defaults to the canonical yoink schema. */
  columns?: SchemaColumn[];
  /** Whether to show the "html / links dropped" footer note. */
  showOmissions?: boolean;
}

export function ParquetSchema({
  columns = defaultColumns,
  showOmissions = true,
}: ParquetSchemaProps) {
  return (
    <DiagramFrame
      label="parquet / flattened schema"
      source="writers.py · Writer.write_parquet"
      caption="snappy-compressed columnar format. portable across pandas / pyarrow / DuckDB / Athena."
    >
      <div className="space-y-3">
        {/* Header strip */}
        <div className="grid grid-cols-[1fr_auto_2fr] gap-3 px-3 pb-2 border-b border-border">
          <span className="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-muted-foreground">
            column
          </span>
          <span className="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-muted-foreground text-right">
            type
          </span>
          <span className="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-muted-foreground">
            note
          </span>
        </div>

        {/* Column rows */}
        <ul className="space-y-px">
          {columns.map((col, i) => (
            <li
              key={col.name}
              className={`grid grid-cols-[1fr_auto_2fr] gap-3 items-baseline px-3 py-2 rounded transition-colors hover:bg-muted/30 ${
                col.highlight ? "bg-amber/[0.04]" : ""
              }`}
            >
              <span className="font-mono text-[0.85rem] text-lime tabular-nums">
                <span className="text-muted-foreground/40 mr-2 select-none">
                  {String(i + 1).padStart(2, "0")}
                </span>
                {col.name}
              </span>
              <span className="font-mono text-[0.78rem] text-cyan text-right whitespace-nowrap">
                {col.type}
              </span>
              <span className="text-[0.78rem] text-muted-foreground">
                {col.note || <span className="text-muted-foreground/30">—</span>}
              </span>
            </li>
          ))}
        </ul>

        {showOmissions && (
          <div className="mt-3 pt-3 border-t border-border flex items-start gap-2.5 px-3">
            <span className="font-mono text-amber text-base leading-none mt-0.5 shrink-0">
              !
            </span>
            <p className="text-[0.8rem] text-foreground/80 leading-relaxed">
              <span className="font-mono text-amber">links</span> and{" "}
              <span className="font-mono text-amber">html</span> are{" "}
              <strong className="text-foreground">dropped</strong> from Parquet output.
              The link <em>count</em> is preserved as{" "}
              <span className="font-mono text-foreground">num_links</span>; raw HTML is
              never written even when{" "}
              <span className="font-mono text-foreground">save_html=True</span>. Use
              JSONL if you need either.
            </p>
          </div>
        )}
      </div>
    </DiagramFrame>
  );
}
