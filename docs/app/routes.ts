import { type RouteConfig, index, layout, route } from "@react-router/dev/routes";

export default [
  // Marketing landing page
  index("routes/_index.tsx"),

  // For LLMs hub — no docs sidebar, has its own TopBar in the route component
  route("llms", "routes/llms.tsx"),

  // LLM-friendly resource routes (text/plain + text/markdown).
  // /docs.md/<slug> serves the raw MDX of a docs page as text/markdown. The
  // dot-in-segment URL keeps splat-at-end matching working without colliding
  // with the existing /docs/* layout route (RR7 splats only match at end of
  // path, so `docs/*.md` is not a usable pattern).
  route("llms.txt", "routes/llms-txt.tsx"),
  route("llms-full.txt", "routes/llms-full-txt.tsx"),
  route("docs.md/*", "routes/docs-md.tsx"),

  // Docs section uses its own layout with sidebar
  layout("routes/docs.tsx", [
    route("docs", "routes/docs._index.tsx"),
    route("docs/*", "routes/docs.$.tsx"),
  ]),
] satisfies RouteConfig;
