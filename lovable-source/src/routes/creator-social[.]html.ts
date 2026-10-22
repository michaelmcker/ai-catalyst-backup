import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/creator-social.html")({
  server: { handlers: siteDocumentHandlers("creator-social.html") },
});
