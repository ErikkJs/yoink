import * as React from "react";
import { cn } from "../../lib/utils";

interface PreProps extends React.HTMLAttributes<HTMLPreElement> {
  raw?: string;
  "data-language"?: string;
  "data-theme"?: string;
}

export function Pre({ children, className, ...props }: PreProps) {
  const ref = React.useRef<HTMLPreElement>(null);
  const [copied, setCopied] = React.useState(false);

  const onCopy = async () => {
    const text = ref.current?.innerText ?? "";
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // noop
    }
  };

  return (
    <div className="group/pre relative">
      <button
        type="button"
        onClick={onCopy}
        className={cn(
          "absolute right-2 top-2 z-10 inline-flex items-center gap-1 rounded-md border border-border/60 bg-card/80 backdrop-blur px-2 py-1 text-[0.7rem] font-medium text-muted-foreground",
          "opacity-0 group-hover/pre:opacity-100 transition-opacity",
          "hover:text-foreground hover:border-border focus:opacity-100"
        )}
        aria-label="Copy code"
      >
        {copied ? (
          <>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="size-3.5">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Copied
          </>
        ) : (
          <>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className="size-3.5">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            Copy
          </>
        )}
      </button>
      <pre ref={ref} className={className} {...props}>
        {children}
      </pre>
    </div>
  );
}
