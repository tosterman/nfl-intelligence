import { test } from "node:test";
import assert from "node:assert/strict";
import Article, { generateMetadata } from "../src/app/[slug]/page";

test("inherited object properties cannot become article routes", async () => {
  for (const slug of ["constructor", "__proto__", "toString", "hasOwnProperty", "not-a-page"]) {
    const params = Promise.resolve({ slug });
    assert.deepEqual(await generateMetadata({ params }), {
      title: "Not found", robots: { index: false },
    });
    await assert.rejects(Article({ params }), (error: unknown) =>
      error instanceof Error && "digest" in error && error.digest === "NEXT_HTTP_ERROR_FALLBACK;404",
    );
  }
});

test("defined articles keep their own canonical metadata", async () => {
  for (const slug of ["about", "privacy", "contact", "responsible-use"]) {
    const metadata = await generateMetadata({ params: Promise.resolve({ slug }) });
    assert.equal(metadata.alternates?.canonical, `/${slug}`);
    assert.notEqual(metadata.title, "Not found");
  }
});
