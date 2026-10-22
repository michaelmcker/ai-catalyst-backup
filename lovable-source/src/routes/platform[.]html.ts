import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/platform.html")({
  server: { handlers: siteDocumentHandlers("platform.html") },
});
