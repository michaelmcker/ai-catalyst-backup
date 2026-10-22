import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/online-conversion.html")({
  server: { handlers: siteDocumentHandlers("online-conversion.html") },
});
