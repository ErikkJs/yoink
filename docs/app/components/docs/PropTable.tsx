import * as React from "react";
import { cn } from "../../lib/utils";

export interface PropRow {
  name: string;
  type: string;
  default?: string;
  description: React.ReactNode;
  required?: boolean;
}

interface PropTableProps {
  rows: PropRow[];
  caption?: string;
  className?: string;
}

export function PropTable({ rows, caption, className }: PropTableProps) {
  return (
    <div className={cn("my-6 overflow-x-auto rounded-lg border border-border-strong", className)}>
      {caption && (
        <div className="px-4 py-2 font-mono text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground bg-muted/40 border-b border-border-strong">
          {caption}
        </div>
      )}
      <table className="w-full text-sm">
        <thead className="bg-muted/30 border-b border-border-strong">
          <tr>
            <th className="text-left font-mono text-[0.68rem] uppercase tracking-[0.12em] text-muted-foreground py-3 px-4">
              Name
            </th>
            <th className="text-left font-mono text-[0.68rem] uppercase tracking-[0.12em] text-muted-foreground py-3 px-4">
              Type
            </th>
            <th className="text-left font-mono text-[0.68rem] uppercase tracking-[0.12em] text-muted-foreground py-3 px-4">
              Default
            </th>
            <th className="text-left font-mono text-[0.68rem] uppercase tracking-[0.12em] text-muted-foreground py-3 px-4">
              Description
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={row.name + i}
              className={cn(
                "align-top transition-colors hover:bg-muted/20",
                i !== rows.length - 1 && "border-b border-border/60"
              )}
            >
              <td className="px-4 py-3 font-mono text-[0.8rem] whitespace-nowrap">
                <span className="text-lime font-medium">{row.name}</span>
                {row.required && (
                  <span className="ml-1 text-amber" title="Required">
                    *
                  </span>
                )}
              </td>
              <td className="px-4 py-3 font-mono text-[0.78rem] text-cyan whitespace-nowrap">
                {row.type}
              </td>
              <td className="px-4 py-3 font-mono text-[0.78rem] text-muted-foreground whitespace-nowrap">
                {row.default ?? <span className="text-muted-foreground/40">—</span>}
              </td>
              <td className="px-4 py-3 text-foreground/85 leading-[1.65]">
                {row.description}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
