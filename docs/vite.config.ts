import { reactRouter } from "@react-router/dev/vite";
import { defineConfig } from "vite";
import { amplifyHosting } from "vite-plugin-react-router-amplify-hosting";
import mdx from "@mdx-js/rollup";
import remarkGfm from "remark-gfm";
import remarkFrontmatter from "remark-frontmatter";
import remarkMdxFrontmatter from "remark-mdx-frontmatter";
import rehypePrettyCode from "rehype-pretty-code";
import { fileURLToPath, URL } from "node:url";

export default defineConfig(({ isSsrBuild }) => ({
  // The `~` alias is declared HERE (not via vite-tsconfig-paths) for two
  // reasons:
  //   1. Linux/CodeBuild's filesystem sometimes makes vite-tsconfig-paths
  //      silently fail to discover tsconfig.json. Build then errors with
  //      "Could not resolve '~/lib/utils'".
  //   2. Even when the plugin DID resolve, it returned the path without
  //      letting Vite's resolve.extensions kick in. Result: ENOENT trying
  //      to open `app/lib/utils` (no extension).
  // Declaring the alias here goes through Vite's normal resolution pipeline
  // (including extension lookup for .ts/.tsx) and works on every platform.
  // tsconfig.json keeps its `paths` entry so VS Code / tsc still resolve
  // imports — they read tsconfig directly, no plugin needed.
  resolve: {
    alias: {
      "~": fileURLToPath(new URL("./app", import.meta.url)),
    },
  },
  plugins: [
    mdx({
      remarkPlugins: [remarkFrontmatter, remarkMdxFrontmatter, remarkGfm],
      rehypePlugins: [
        [
          rehypePrettyCode,
          {
            theme: "github-dark",
            keepBackground: true,
          },
        ],
      ],
    }),
    reactRouter(),
    amplifyHosting(),
  ],
  // SSR-only: inline every dynamic import into server.mjs.
  // Otherwise Vite splits server code into multiple `assets/*.mjs` chunks,
  // and `vite-plugin-react-router-amplify-hosting` only copies `server.mjs`
  // to the deploy bundle — at runtime Lambda throws ERR_MODULE_NOT_FOUND.
  // (Pattern borrowed from stax/apps/web.)
  build: isSsrBuild
    ? { rollupOptions: { output: { inlineDynamicImports: true } } }
    : {},
}));
