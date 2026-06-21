# Dashboard (Evidence.dev)

A SQL-to-static-site BI app over the dbt marts, themed to the Sam Malik design
system (terminal-meets-gothic: void ground, phosphor signal, oxblood literary).

## Run it locally

The warehouse must exist first (`make build` from the repo root builds
`warehouse/ddf.duckdb`). Then:

```bash
cd dashboard
npm install
npm run sources   # materialize the source queries from DuckDB
npm run dev       # serve at http://localhost:3000
```

Build the static site for deploy:

```bash
npm run build     # outputs to dashboard/build/
```

## Layout

- `sources/ddf/connection.yaml` — DuckDB connection to `../warehouse/ddf.duckdb`.
- `sources/ddf/*.sql` — one query per mart/view; each becomes `ddf.<name>` in pages.
  All seven were verified to run against the warehouse.
- `pages/` — `index` (overview + uncertainty), `reconciliation`, `regional`,
  `recovery`.
- `evidence.config.yaml` — dark appearance + on-brand chart palette.
- `static/theme.css` — design tokens + fonts, for deeper custom styling.

## Deploy (Phase 6)

Point the deployed site at the **BigQuery** prod target (de-identified marts only)
so the public dashboard reads from the cloud warehouse while local dev stays on
DuckDB. Netlify or GitHub Pages both serve the static `build/` output.

## Notes

- Version pins in `package.json` are a reasonable baseline; if the Evidence CLI
  has moved, scaffold a fresh project with `npx degit evidence-dev/template .`
  and drop `pages/` + `sources/` in — the SQL and content are framework-stable.
- `node_modules/`, `.evidence/`, and `build/` are gitignored.
