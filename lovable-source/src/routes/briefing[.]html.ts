import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/briefing.html")({
  server: { handlers: siteDocumentHandlers("briefing.html") },
});
