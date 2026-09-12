# Domain Docs

**Layout:** single-context

- `CONTEXT.md` at repo root — glossary of domain terms + decisions
- `docs/adr/` at repo root — architecture decision records

Consumer rules: `grill-with-docs` reads/updates `CONTEXT.md` each session; treat it as the source of truth for terminology over any stale comment or doc.
