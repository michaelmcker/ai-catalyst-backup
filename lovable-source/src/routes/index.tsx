import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

// "/" returns the original approved home document unchanged.
export const Route = createFileRoute("/")({
  server: { handlers: siteDocumentHandlers("index.html") },
});
