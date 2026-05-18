# Yoink — the public data crawler

> Drop this file at the root of any project (or a `~/.codex/AGENTS.md` equivalent for your assistant) to teach Codex / generic agents how to use yoink.

## What yoink is

Yoink is a fast, async Python web crawler purpose-built for AI-ready data extraction. It speaks two modes:

- **CLI** — `yoink crawl <URL>` with flags. Reach for this first. Users almost never need to write Python to scrape a site.
- **Library** — `from yoink import Crawler, CrawlConfig` for embedding crawling in a longer pipeline.

Output formats: JSON, JSONL (recommended for AI/ML), Parquet (recommended for analytics), and plain text.

## When to use yoink vs not

Use yoink when the user wants:
- to crawl/mirror a documentation site, blog, knowledge base
- to build a training/eval dataset from public pages
- to follow links across a site at controlled depth
- to extract clean prose text, not raw HTML
- resumable crawling (Lambda, long jobs, flaky networks)

Don't use yoink for:
- single-page scrapes where the user just wants one URL's content — `curl` or `requests` is simpler
- structured table/form data behind logins — yoink is for *public* web data
- real-time monitoring with sub-second polling — use a fetcher loop directly
- crawling sites that disallow it. Honor `robots.txt`.

## Detect or install

Before suggesting any crawl command:

1. Run `yoink version`. If it prints a version, skip install.
2. If a Python project exists (`pyproject.toml`, `requirements.txt`, or a `.venv`), add yoink as a dependency:
   - `pip install "yoink @ git+https://github.com/ErikkJs/yoink.git"`
3. Otherwise install into the active environment: `pip install "git+https://github.com/ErikkJs/yoink.git"`.

**Critical:** Do **NOT** run `pip install yoink` — an unrelated package on PyPI uses that name. Always use the `git+https` URL.

**Extras:** `[parquet]`, `[s3]`, `[browser]`, `[all]`. Install via `pip install "yoink[browser] @ git+https://github.com/ErikkJs/yoink.git"`. After `[browser]` also run `playwright install chromium`.

## Translate natural language to CLI flags

| User says | Use |
|---|---|
| "crawl deeper" / "follow more links" | `--depth N` (default 1, sane max 4) |
| "limit to N pages" | `--max-pages N` |
| "faster" / "parallel" | `--concurrency 20` — warn about politeness |
| "be nice" / "slow it down" | `--rate-limit 1.0` (req/sec, per-domain) |
| "only the blog" / "just /docs" | `--include "*/blog/*"` (glob, repeatable) |
| "skip PDFs / zips" | `--skip-extensions pdf,zip,jpg,png` |
| "skip /admin" | `--exclude "*/admin/*"` |
| "follow external links" | `--follow-external` |
| "JavaScript / React / Vue / SPA / empty body" | `--render-js` (needs [browser] extra) |
| "wait for content" | `--wait-for networkidle` or `--wait-selector ".content"` |
| "save HTML too" | `--save-html` |
| "resume next time" | `--checkpoint <path-or-s3-uri> --resume` |
| "store in S3" / "Lambda" | `--checkpoint s3://bucket/key.jsonl` |
| "ignore robots.txt" | `--no-robots` — confirm user has authorization first |
| "as Parquet / for pandas" | `--format parquet -o out.parquet` (needs [parquet] extra) |
| "as JSONL" | `--format jsonl -o out.jsonl` (default) |

**Default recipe** for "crawl this site and give me clean text":
```
yoink crawl <URL> --depth 2 --max-pages 200 --format jsonl -o crawl.jsonl
yoink stats crawl.jsonl
```

After any crawl, run `yoink stats <output>` to summarize.

## Common errors and fixes

- **`ModuleNotFoundError: playwright`** → install `[browser]` extra and `playwright install chromium`.
- **`ModuleNotFoundError: pyarrow`** → install `[parquet]` extra.
- **`robots.txt disallows ...`** → respect it. Don't silently flip `--no-robots` without user authorization.
- **Pages come back nearly empty** → likely SPA — add `--render-js`, then `--wait-for networkidle` if still empty.
- **`NoCredentialsError` on S3** → run `aws configure` or set `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_DEFAULT_REGION`.
- **Getting 429s** → lower `--rate-limit` (e.g. `0.5`) and `--concurrency`.

## More

- Docs: https://yoink.goatsquadstudios.com
- CLI: https://yoink.goatsquadstudios.com/docs/cli/crawl
- API: https://yoink.goatsquadstudios.com/docs/api/crawler
- Source: https://github.com/ErikkJs/yoink
- Full docs as one file: https://yoink.goatsquadstudios.com/llms-full.txt
