import { Link } from "react-router";
import type { MDXComponents } from "mdx/types";
import { Pre } from "./CodeBlock";
import { Callout } from "./Callout";
import { PropTable } from "./PropTable";
import {
  TokenBucket,
  CrawlLifecycle,
  RobotsFlow,
  FetcherDispatch,
  CheckpointRecords,
  URLFilterPipeline,
  LambdaArchitecture,
  Pipeline,
  ParquetSchema,
} from "./diagrams";

export const mdxComponents: MDXComponents = {
  pre: Pre as any,
  a: ({ href = "", children, ...props }) => {
    if (href.startsWith("http") || href.startsWith("mailto:")) {
      return (
        <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
          {children}
        </a>
      );
    }
    return (
      <Link to={href} {...(props as any)}>
        {children}
      </Link>
    );
  },
  Callout,
  PropTable,
  TokenBucket,
  CrawlLifecycle,
  RobotsFlow,
  FetcherDispatch,
  CheckpointRecords,
  URLFilterPipeline,
  LambdaArchitecture,
  Pipeline,
  ParquetSchema,
};
