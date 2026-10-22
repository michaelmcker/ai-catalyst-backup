<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

## Project rules
- The site is the original static HTML/CSS/JS kept byte-for-byte: the nine HTML pages in `site/`, every other file in `public/` at its original path. Never edit, reformat, or re-encode them — they are the approved source of truth.
- `src/lib/site-documents.ts` plus one `src/routes/<page>[.]html.ts` per page (and `index.tsx` for `/`) is the only serving adapter; pages are returned raw from the runtime because the host's static layer rewrites `.html` URLs, which would break original paths.
- Do not add React pages, iframes, or redirects for the site's pages; they would diverge from the approved documents.
