# yoink-docs

Documentation site for [yoink](https://github.com/ErikkJs/yoink) — the public data crawler.

Built with React Router 7 (SSR), Vite, Tailwind, shadcn/ui, MDX, and deployed on AWS Amplify Hosting.

## Develop

```bash
cd docs
npm install --legacy-peer-deps
npm run dev
```

Open <http://localhost:5173>.

## Build

```bash
npm run build
npm start
```

## Deploy

Push to the connected Amplify branch. The `amplify.yml` at the repo root handles the build pipeline.

## Project layout

```
app/
├── app.css                 # Tailwind + theme tokens
├── root.tsx                # HTML shell, dark mode, fonts
├── routes.ts               # Route table
├── components/
│   ├── ui/                 # shadcn primitives (button, card, badge, separator, tooltip)
│   ├── layout/             # DocsLayout, Sidebar, TopBar
│   └── docs/               # CodeBlock, Callout, PropTable, MDXComponents
├── content/docs/           # MDX content (concepts, cli, api, examples)
├── data/nav.ts             # Sidebar navigation tree
├── lib/                    # Utils + MDX loader
└── routes/                 # File-based routes (landing + docs)
```

Add a new docs page by creating an MDX file in `app/content/docs/<section>/<slug>.mdx` and registering it in `app/data/nav.ts`.
