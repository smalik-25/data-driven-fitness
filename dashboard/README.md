# Dashboard (Evidence.dev)

A SQL-to-static-site BI app over the dbt marts, themed to the Sam Malik design
system (terminal-meets-gothic: void ground, phosphor signal, oxblood literary).

## Data source

Evidence reads `sources/ddf/public.duckdb` — a small, **committed**, de-identified
DuckDB holding only the aggregate marts/dims the pages query (no raw data, no
bronze, nothing PII). It's produced from the full local warehouse by:

```bash
make export-public      # warehouse/ddf.duckdb -> dashboard/sources/ddf/public.duckdb
```

Because it's committed, both local dev and Netlify CI build from it identically,
and anyone who clones the repo can build the site without the raw data.

## Run it locally

```bash
# from the repo root, after `make build` (which builds the warehouse):
make export-public          # refresh the committed public DB
cd dashboard
npm install                 # use Node 20 (nvm use 20); Node 24 hangs Evidence's Vite
npm run sources             # materialize the source queries from public.duckdb
npm run dev                 # serve at http://localhost:3000
```

Build the static site:

```bash
npm run build               # outputs to dashboard/build/
```

## Layout

- `sources/ddf/connection.yaml` — DuckDB connection to the committed `public.duckdb`.
- `sources/ddf/*.sql` — one query per mart; each becomes `ddf.<name>` in pages.
- `pages/` — `index`, `reconciliation`, `regional`, `recovery`, plus `about`,
  `methods`, `data-dictionary`.
- `evidence.config.yaml` — plugins + dark appearance.
- `static/theme.css` — design tokens + fonts.

## Deploy (Netlify, auto-build on push)

`netlify.toml` (repo root) builds from the committed `public.duckdb`, so no data
or secrets are needed in CI:

1. Push to GitHub.
2. In Netlify: **Add new site → Import from Git**, pick the repo. The build
   settings come from `netlify.toml` (base `dashboard`, build `npm install &&
   npm run sources && npm run build`, publish `build`, Node 20).
3. Every push to the default branch redeploys. To refresh the data, run
   `make build && make export-public`, commit the updated `public.duckdb`, push.

## Notes

- Node **20** required (Node 24 hangs Evidence's Vite pre-bundle). `netlify.toml`
  pins `NODE_VERSION = "20"` for CI.
- `node_modules/`, `.evidence/`, and `build/` are gitignored; `public.duckdb` is
  explicitly tracked (gitignore exception).
