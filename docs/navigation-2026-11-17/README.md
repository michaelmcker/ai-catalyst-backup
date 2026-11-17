# Compact navigation — 17 November 2026

Reduced expanded-menu main labels to 24px on desktop and 20px on phones, with 16px nested labels and tighter spacing. Views up to 760px high use 18px/14px text and shorter rows. A viewport-height cap and emergency overflow remain for unusually short windows or enlarged text; content is never deliberately clipped to conceal scrolling.

Verified the fully opened menu after its animation completed: 84 cases spanning all four languages, three page shells (home, blog, service), and seven viewport sizes down to 320×568. No panel overflow, clipped links or offscreen panel bottom. Hosted preview: eight desktop/phone cases, all passed.

Localization, blog and public-site checks, source reproducibility and preference-switcher tests passed. The enclosing portfolio npm suite retained the same two existing failures before and after (168/170 passed).

Preview deployment: 81075837-ce6b-4258-ae28-8801056fd14d.
