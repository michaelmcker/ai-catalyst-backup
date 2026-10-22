import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/index.html")({
  server: { handlers: siteDocumentHandlers("index.html") },
});
