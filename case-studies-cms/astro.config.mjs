import cloudflare from "@astrojs/cloudflare";
import react from "@astrojs/react";
import { d1 } from "@emdash-cms/cloudflare";
import { defineConfig } from "astro/config";
import emdash from "emdash/astro";

export default defineConfig({
	output: "server",
	adapter: cloudflare({imageService: "passthrough"}),
	site: "https://aicatalyst.biz",
	image: {
		layout: "constrained",
		responsiveStyles: true,
	},
	integrations: [
		react(),
		emdash({
			siteUrl: "https://aicatalyst.biz",
			admin: {locales: ["en"]},
			database: d1({ binding: "DB", session: "auto", coalesce: true }),
		}),
	],
	devToolbar: { enabled: false },
});
