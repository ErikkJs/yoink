import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-foreground text-background",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        lime: "border-lime/30 bg-lime/10 text-lime",
        cyan: "border-cyan/30 bg-cyan/10 text-cyan",
        amber: "border-amber/30 bg-amber/10 text-amber",
        magenta: "border-magenta/30 bg-magenta/10 text-magenta",
        // back-compat aliases
        emerald: "border-lime/30 bg-lime/10 text-lime",
        purple: "border-magenta/30 bg-magenta/10 text-magenta",
        blue: "border-cyan/30 bg-cyan/10 text-cyan",
        outline: "border-border bg-card text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
