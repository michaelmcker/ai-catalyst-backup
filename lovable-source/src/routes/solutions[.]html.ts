import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/solutions.html")({
  server: { handlers: siteDocumentHandlers("solutions.html") },
});
