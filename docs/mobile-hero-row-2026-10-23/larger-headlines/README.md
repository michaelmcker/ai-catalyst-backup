# Larger mobile headlines and shorter complete subheads

The user requested bigger headlines with fewer lines on the kneeling-knight How We Work page and the visible-face Training page, and authorized shorter supporting sentences. These two headings now occupy 74% of the reading width and use a larger fluid type size. The kneeling artwork moves modestly right/down so its helmet and hands remain clear. Company keeps its previous mobile composition. Desktop/tablet heading styles and the shared renderer are unchanged.

The complete subheads remain full-width below the entire headline/image row:

- How We Work: “We pair senior operators with validated AI in a focused pilot, with initial Full Commerce MMM findings in 2–6 weeks.”
- Training: “Practical training gives your team usable tools, a shared way to assess AI output and workflows they can run.”

The two explicit paragraphs are the only new copy exceptions in the source verifier and the row checker. Headline and action wording remains unchanged. CSS uses `20261023-row2` on the three existing row pages.

`candidate.json` and 12 page captures cover Company, Solutions and Training at 320/390/430/600 CSS pixels, DPR3. `results.json` passes approved text completeness, unclipped character bounds, full-width uninterrupted paragraphs, >=20px image-to-paragraph separation and actual protected source-ink clearance. Self-tests reject changed copy, clipped characters, paragraph gaps, narrowed paragraphs and source-ink collisions.

Two `native-safari-*-390.png` captures show the actual macOS Safari Responsive Design Mode rendering of the changed pages. They are visual review evidence, not physical iPhone verification. Deployment metadata and live source checks follow publication. Production remains unchanged while the user checks the preview.
