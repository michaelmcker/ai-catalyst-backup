# Contact and navigation release — 23 October 2026

The user's supplied feedback requests removal of every public LinkedIn route, including the founder and five advisor profile links; direct email/phone contact; removal of Catalyst Retail Solutions references; and Training and adoption immediately after How We Work in all nine expanded menus.

## Implemented

- All nine public pages use `mailto:randy@aicatalyst.biz` and `tel:+14162700132`, with Toronto, Canada retained.
- Homepage contact uses an Email Randy action, the visible email address, phone and location. Other contact sections use the same address and phone. Every footer includes the direct email link.
- Founder and advisor LinkedIn profile links are removed. No LinkedIn or Catalyst Retail Solutions reference remains in deployed HTML or JavaScript, including the unconfigured-form fallback.
- Every expanded menu includes Training and adoption linked to `training.html`, immediately after How We Work.
- The two approved hero primitives and original media are retained. Matching root public files mirror `current-site/`. The Lovable export remains historical.

## Verification

`python3 scripts/check-public-site.py` passes for all nine pages, contact/footer completeness, navigation order, retired references, local links and fifteen JavaScript syntax checks. It reproduced the missing routes/menu links before implementation.

`rendered-checks.json` records 36 browser checks: all nine pages at 1440, 768, 390 and 320px, without horizontal overflow, clipped email addresses, incorrect menu order, LinkedIn routes or hero layout regressions. The expanded mobile menu and homepage email/phone composition were visually reviewed.

## Mailbox status, separate from website changes

Public DNS on October 23 uses `dns1.registrar-servers.com` / `dns2.registrar-servers.com`, with five `eforward*.registrar-servers.com` MX records. Randy's Cloudflare zone is pending activation and contains the same forwarding MX records. This establishes registrar forwarding configuration, not a verified Google Workspace mailbox or delivery to this specific address. No DNS, forwarding, mailbox, billing or Workspace account changes were made. The user was asked whether the mailbox already receives mail.
