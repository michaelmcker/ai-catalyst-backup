import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/marketing-investment.html")({
  server: { handlers: siteDocumentHandlers("marketing-investment.html") },
});
