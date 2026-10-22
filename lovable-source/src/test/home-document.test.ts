import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { siteDocumentHandlers, siteDocuments, type SiteDocumentName } from "@/lib/site-documents";
import { Route as HomeRoute } from "@/routes/index";

const pages = Object.keys(siteDocuments) as SiteDocumentName[];

async function bytes(res: Response) {
  return Buffer.from(new Uint8Array(await res.arrayBuffer()));
}

describe("approved site documents", () => {
  it("serves all nine original pages", () => {
    expect(pages.sort()).toEqual(
      [
        "briefing.html",
        "company.html",
        "creator-social.html",
        "index.html",
        "marketing-investment.html",
        "online-conversion.html",
        "platform.html",
        "solutions.html",
        "training.html",
      ].sort(),
    );
  });

  it.each(pages)("serves %s byte for byte as a full HTML page", async (name) => {
    const res = siteDocumentHandlers(name).GET();
    const original = readFileSync(resolve(__dirname, "../../site", name));
    expect(res.headers.get("content-type")).toBe("text/html; charset=utf-8");
    expect((await bytes(res)).equals(original)).toBe(true);
  });

  it("serves the original home page at /", async () => {
    const handlers = HomeRoute.options.server?.handlers as { GET: () => Response };
    const original = readFileSync(resolve(__dirname, "../../site/index.html"));
    expect((await bytes(handlers.GET())).equals(original)).toBe(true);
  });
});
