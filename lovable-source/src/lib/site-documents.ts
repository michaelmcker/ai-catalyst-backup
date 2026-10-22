// Serving adapter for the approved static site. The nine original HTML
// documents live unchanged in /site and are returned as-is, as full pages,
// at their original paths. Every other file is served from public/.
import briefing from "../../site/briefing.html?raw";
import company from "../../site/company.html?raw";
import creatorSocial from "../../site/creator-social.html?raw";
import index from "../../site/index.html?raw";
import marketingInvestment from "../../site/marketing-investment.html?raw";
import onlineConversion from "../../site/online-conversion.html?raw";
import platform from "../../site/platform.html?raw";
import solutions from "../../site/solutions.html?raw";
import training from "../../site/training.html?raw";

export const siteDocuments = {
  "index.html": index,
  "platform.html": platform,
  "creator-social.html": creatorSocial,
  "online-conversion.html": onlineConversion,
  "marketing-investment.html": marketingInvestment,
  "company.html": company,
  "solutions.html": solutions,
  "training.html": training,
  "briefing.html": briefing,
} as const;

export type SiteDocumentName = keyof typeof siteDocuments;

const htmlHeaders = { "content-type": "text/html; charset=utf-8" };

export function siteDocumentHandlers(name: SiteDocumentName) {
  return {
    GET: () => new Response(siteDocuments[name], { headers: htmlHeaders }),
    HEAD: () => new Response(null, { headers: htmlHeaders }),
  };
}
