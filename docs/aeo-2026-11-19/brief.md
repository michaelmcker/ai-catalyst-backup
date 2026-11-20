# Coffee Chats retrieval brief
Audience: business leaders selecting measurement, agentic selling or practical AI training support. Entity: AI Catalyst, with Randy Weyersberg as named author/speaker.

| Chat | Main retrieval question | Secondary questions |
|---|---|---|
| MMM | How can a CMO connect marketing spend to the next business decision? | Which spend lines count? Which three measurement questions matter? How should insight lead to action? |
| Agentic Live Selling | How does a brand agent support shopping and live selling? | What is one-to-one versus one-to-many? Who attends a live show? What should a storefront agent know? |
| AI Training | How can AI training change actual workflows? | What is built in a session? Where does human judgment remain? Which teams and delivery formats are supported? |

Primary evidence: each published YouTube recording and its captions; the supplied AI Training DOCX resolves terms without replacing recording evidence. Existing training and service pages supply internal next steps. No competitor claims or keyword-volume assertions are needed for this source-led update. Summaries and FAQs must not promote unsupported statistics or guarantee performance. Transcript claims remain the speaker's words, not independently established editorial facts.

Implementation: visible answer-first summary before the video; three visible questions at the end of each article; locale-specific canonical/hreflang, metadata, BlogPosting, BreadcrumbList, FAQPage and site entity JSON-LD derived from visible copy; crawlable text plus deterministic robots.txt and llms discovery exports. Existing URLs remain stable. No promise of LLM inclusion or rich results.

Editor gate: source/summary/FAQ parity, all-language completeness, visible/schema text equality, factual dates, preserved safety/human-review boundaries, restrained CTA, responsive proof, hosted crawl-file verification.

Baseline audit: robots.txt, llms.txt and llms-full.txt returned HTTP 200 but contained the homepage HTML fallback, not crawler files. sitemap.xml was actual XML; no JSON-LD existed in public HTML. The Cloudflare bot-management configuration had AI/search/user bot blocking disabled and no custom zone ruleset. The release adds actual text files and schema without changing security settings.

Editorial review: summaries/FAQs were checked against the published caption sources; no unsourced percentages or market claims were promoted into the new editorial answer blocks. The AI Training source DOCX confirms the caption correction “Not notes. Not a demo.” and site spelling. The requested existing transcript-note removal stays respected. Translation review is model review, not native-speaker certification.

Schema is JSON-LD with Organization, Person, WebSite and WebPage on all public pages; Coffee Chats add BlogPosting, BreadcrumbList, VideoObject and FAQPage where applicable. FAQ schema matches three visible answers per article. Video upload dates were not independently established, so none is invented; VideoObject presence does not mean Google video-rich-result eligibility was certified. No rich-result or LLM citation guarantee is made.

Reference guidance checked: https://developers.google.com/search/docs/appearance/structured-data/article ; https://developers.openai.com/api/docs/bots ; https://llmstxt.org/ .

Release verification: 60 localized article viewport checks (three posts × four editions × five widths) passed without detected horizontal overflow or clipped text. Every article had an upfront summary and three FAQ items. Live English AI Training heading, summary, three FAQs and the correct video were observed in the in-app browser. Preview and live text/Markdown MIME checks passed. Live HTTP checks covered all 12 article editions plus robots.txt, llms.txt, llms-full.txt, sitemap.xml and the new English Markdown source. Portfolio npm suite retained its same two existing failures before and after (168/170).

Preview: e029fbcf-853f-4c97-b2bc-7360854f8611.
Production: 5e7441fd-2487-4c20-a29a-1b702cfc670a.
