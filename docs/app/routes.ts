import { type RouteConfig, index, layout, route } from "@react-router/dev/routes";

export default [
  // Marketing landing page
  index("routes/_index.tsx"),

  // Docs section uses its own layout with sidebar
  layout("routes/docs.tsx", [
    route("docs", "routes/docs._index.tsx"),
    route("docs/*", "routes/docs.$.tsx"),
  ]),
] satisfies RouteConfig;
