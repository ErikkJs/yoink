import type { TocEntry } from "../components/docs/TableOfContents";

export interface DocFrontmatter {
  title: string;
  description?: string;
  category?: string;
}

interface DocModule {
  default: React.ComponentType<{ components?: Record<string, unknown> }>;
  frontmatter?: DocFrontmatter;
  tableOfContents?: TocEntry[];
}

const docModules = import.meta.glob<DocModule>("../content/docs/**/*.mdx", {
  eager: true,
});

function pathToSlug(path: string): string {
  return path.replace("../content/docs/", "").replace(/\.mdx$/, "");
}

export interface LoadedDoc {
  slug: string;
  frontmatter: DocFrontmatter;
  Component: React.ComponentType<{ components?: Record<string, unknown> }>;
  toc: TocEntry[];
}

export function getDoc(slug: string): LoadedDoc | null {
  const target = `../content/docs/${slug}.mdx`;
  const mod = docModules[target];
  if (!mod) return null;
  return {
    slug,
    frontmatter: mod.frontmatter ?? { title: slug },
    Component: mod.default,
    toc: mod.tableOfContents ?? [],
  };
}

export function listDocs(): { slug: string; frontmatter: DocFrontmatter }[] {
  return Object.entries(docModules).map(([path, mod]) => ({
    slug: pathToSlug(path),
    frontmatter: mod.frontmatter ?? { title: pathToSlug(path) },
  }));
}
