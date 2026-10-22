import { createFileRoute } from "@tanstack/react-router";

import { siteDocumentHandlers } from "@/lib/site-documents";

export const Route = createFileRoute("/training.html")({
  server: { handlers: siteDocumentHandlers("training.html") },
});
