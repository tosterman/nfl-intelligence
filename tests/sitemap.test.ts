import assert from "node:assert/strict";
import test from "node:test";
import sitemap from "../src/app/sitemap";
import { teams } from "../src/lib/teams";

test("sitemap includes every canonical lowercase team route exactly once", () => {
  const entries = sitemap();
  const paths = entries.map((entry) => new URL(entry.url).pathname);
  for (const code of Object.keys(teams)) {
    assert.equal(
      paths.filter((path) => path === `/teams/${code.toLowerCase()}`).length,
      1,
    );
  }
  assert.equal(new Set(entries.map((entry) => entry.url)).size, entries.length);
});

test("policy pages do not inherit forecast update dates", () => {
  for (const entry of sitemap()) {
    const path = new URL(entry.url).pathname;
    if (
      [
        "/privacy",
        "/about",
        "/contact",
        "/responsible-use",
        "/methodology",
      ].includes(path)
    ) {
      assert.equal(entry.lastModified, undefined);
    } else {
      assert.ok(entry.lastModified instanceof Date);
      assert.ok(Number.isFinite(entry.lastModified.getTime()));
    }
  }
});
