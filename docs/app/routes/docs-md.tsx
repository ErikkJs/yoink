import type { Route } from "./+types/docs-md";
import { getRawDoc } from "../lib/docs-raw.server";

// Resource route — no default export, so RR7 returns the loader's Response
// directly without wrapping it in the React tree. Mounted at `/docs.md/<slug>`
// in routes.ts. The dot-in-segment URL avoids colliding with the existing
// `/docs/*` layout route (RR7 splats only match at the end of a path, so
// `/docs/*.md` cannot be expressed as a route pattern).

type SplatParams = { "*"?: string };

export async function loader({ params }: Route.LoaderArgs) {
  const slug = (params as SplatParams)["*"] ?? "";
  if (!slug) {
    throw new Response("Not Found", { status: 404 });
  }
  const raw = getRawDoc(slug);
  if (raw === null) {
    throw new Response("Not Found", { status: 404 });
  }
  return new Response(raw, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Cache-Control": "public, max-age=300",
    },
  });
}
