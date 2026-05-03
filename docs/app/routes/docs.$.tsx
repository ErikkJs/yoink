import { useParams } from "react-router";
import { useMemo } from "react";
import type { Route } from "./+types/docs.$";
import { getDoc } from "../lib/docs.server";
import { findNavItem } from "../data/nav";
import { mdxComponents } from "../components/docs/MDXComponents";
import { TableOfContents } from "../components/docs/TableOfContents";
import { PrevNext } from "../components/docs/PrevNext";

export async function loader({ params }: Route.LoaderArgs) {
  const slug = params["*"] ?? "";
  if (!slug) {
    throw new Response("Not Found", { status: 404 });
  }
  const doc = getDoc(slug);
  if (!doc) {
    throw new Response("Not Found", { status: 404 });
  }
  const navContext = findNavItem(slug);
  return {
    slug,
    frontmatter: doc.frontmatter,
    toc: doc.toc,
    section: navContext?.section.title ?? null,
    prev: navContext?.prev ?? null,
    next: navContext?.next ?? null,
  };
}

export function meta({ data }: Route.MetaArgs) {
  if (!data) return [{ title: "Docs — yoink" }];
  return [
    { title: `${data.frontmatter.title} — yoink docs` },
    {
      name: "description",
      content: data.frontmatter.description ?? "yoink documentation",
    },
  ];
}

const docModules = import.meta.glob<{
  default: React.ComponentType<{ components?: Record<string, unknown> }>;
}>("../content/docs/**/*.mdx", { eager: true });

export default function DocsPage({ loaderData }: Route.ComponentProps) {
  const { slug, frontmatter, toc, section, prev, next } = loaderData;
  const params = useParams();
  const currentSlug = params["*"] ?? slug;

  const Content = useMemo(() => {
    const path = `../content/docs/${currentSlug}.mdx`;
    return docModules[path]?.default ?? null;
  }, [currentSlug]);

  return (
    <div className="mx-auto w-full max-w-[96rem] px-6 lg:px-12 py-12 lg:py-14 grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_240px] 2xl:grid-cols-[minmax(0,1fr)_260px] gap-10 xl:gap-14">
      <article className="min-w-0 animate-fade-up @container/article">
        <header className="mb-10 pb-8 border-b border-border">
          {section && (
            <p className="meta-pill mb-4 text-lime">
              <span className="size-1 rounded-full bg-lime" />
              {section}
            </p>
          )}
          <h1 className="font-display text-4xl md:text-[2.75rem] font-bold tracking-tight text-foreground leading-[1.05]">
            {frontmatter.title}
          </h1>
          {frontmatter.description && (
            <p className="mt-4 text-lg text-muted-foreground leading-[1.55] max-w-2xl">
              {frontmatter.description}
            </p>
          )}
          <div className="mt-6 flex items-center gap-4 font-mono text-[0.65rem] text-muted-foreground/60">
            <span>docs/{currentSlug}.mdx</span>
            <span className="text-border-strong">·</span>
            <a
              href={`https://github.com/ErikkJs/yoink/edit/main/docs/app/content/docs/${currentSlug}.mdx`}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-lime transition-colors inline-flex items-center gap-1"
            >
              edit on github ↗
            </a>
          </div>
        </header>

        <div className="prose-docs">
          {Content ? <Content components={mdxComponents as any} /> : null}
        </div>

        <PrevNext prev={prev} next={next} />
      </article>

      <aside className="hidden xl:block sticky top-20 self-start max-h-[calc(100vh-6rem)] overflow-y-auto pr-2">
        <TableOfContents entries={toc} />
      </aside>
    </div>
  );
}
