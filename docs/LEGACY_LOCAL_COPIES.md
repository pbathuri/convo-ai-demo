# Legacy local copies (not in this repo)

This repository **[pbathuri/convo-ai-demo](https://github.com/pbathuri/convo-ai-demo)** is the **single canonical** source for Convo AI. During development, the same project was copied into several folders on the author’s machine. Those paths are **not** tracked here and may be **out of date** or **identical** to an older snapshot.

If you find multiple `convo-ai` folders on disk, use **only the clone of this GitHub repo** for work, and treat the others as backups or stale copies you can remove after verifying you do not need local-only changes.

## Observed duplicate project roots (historical)

These directories were reported as containing a `convo-ai` app layout (Streamlit app, `app/`, `components/`, etc.):

| Location | Notes |
|----------|--------|
| `~/Desktop/Liesure_Projects/Personal_prjs/convo-ai` | Alternate copy alongside other Personal_prjs work. |
| `~/Desktop/Liesure_Projects/Personal_prjs/Personal_prjs/convo-ai` | Nested `Personal_prjs` path; easy duplicate from moving folders. |
| `~/Desktop/Liesure_Projects/Personal_prjs/Computer Data COLLECTION/Personal_prjs/convo-ai` | Original workstation path used to prepare the first GitHub push; may still exist locally. |

**Rule of thumb:** After `git clone https://github.com/pbathuri/convo-ai-demo.git`, work inside that clone. Delete or archive old folders only after you confirm no uncommitted edits live there (compare with `git status` / diff, or copy any unique files into the repo first).

## Related content (not duplicate codebases)

These are **not** full app copies; they are publishing or marketing assets that were **consolidated** into this repo under `materials/`:

| Original area | Now in repo |
|----------------|-------------|
| `Website_Per/publish_ready/wix_blog_posts/convo-ai-build-loop/` | `materials/wix-blog/convo-ai-build-loop/` |
| `Website_Per/publish_ready/wix_media/convo-ai-build-loop/` | Cover image co-located with the blog draft in `materials/wix-blog/convo-ai-build-loop/` |
| Desktop `CONVO-Marketing App` (inside an old convo-ai folder) | `materials/marketing/` |

See [materials/README.md](../materials/README.md) for file-level descriptions.

## Keeping documentation honest

- Update **this file** if you retire old paths or add new canonical locations.
- Prefer linking to **GitHub** in READMEs and portfolios instead of absolute paths on one machine.
