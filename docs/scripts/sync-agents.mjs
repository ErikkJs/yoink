#!/usr/bin/env node
// Copies agents/yoink/* from repo root → docs/public/agents/yoink/* so the docs
// site can serve them as static downloads. Runs as `prebuild` and can be invoked
// manually during dev to refresh the public mirror.

import { mkdirSync, readdirSync, copyFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const src = join(repoRoot, "agents", "yoink");
const dest = join(repoRoot, "docs", "public", "agents", "yoink");

function copyDir(from, to) {
  mkdirSync(to, { recursive: true });
  for (const entry of readdirSync(from)) {
    const fromPath = join(from, entry);
    const toPath = join(to, entry);
    const stat = statSync(fromPath);
    if (stat.isDirectory()) {
      copyDir(fromPath, toPath);
    } else {
      copyFileSync(fromPath, toPath);
    }
  }
}

try {
  copyDir(src, dest);
  console.log(`[sync-agents] copied ${src} → ${dest}`);
} catch (err) {
  console.error(`[sync-agents] failed: ${err.message}`);
  process.exit(1);
}
