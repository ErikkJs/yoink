import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "../../lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-foreground text-background hover:bg-foreground/90 shadow-sm",
        lime:
          "bg-lime text-background font-semibold hover:bg-lime-bright shadow-[0_0_0_1px_hsl(var(--lime)/0.6),0_8px_24px_-8px_hsl(var(--lime)/0.5)] hover:shadow-[0_0_0_1px_hsl(var(--lime)/0.8),0_12px_32px_-8px_hsl(var(--lime)/0.7)] transition-shadow",
        // alias kept for any older references
        emerald:
          "bg-lime text-background font-semibold hover:bg-lime-bright shadow-[0_0_0_1px_hsl(var(--lime)/0.6),0_8px_24px_-8px_hsl(var(--lime)/0.5)]",
        outline:
          "border border-border bg-card hover:bg-muted hover:border-border-strong hover:text-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-muted/60 hover:text-foreground",
        link: "text-lime underline-offset-4 hover:underline",
        destructive:
          "bg-destructive/10 text-destructive border border-destructive/30 hover:bg-destructive/20",
      },
      size: {
        default: "h-9 px-4 py-2",
        xs: "h-7 px-2.5 text-xs",
        sm: "h-8 px-3 text-xs",
        lg: "h-11 px-6 text-base",
        icon: "size-9",
        "icon-sm": "size-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
