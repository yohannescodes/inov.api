# Novarch Backend

FastAPI API serving content for novarch.lol. Public entry endpoints now source data directly from the Novarch Sanity Studio (`novarch-cms`).

## Requirements

- Python 3.11+
- PostgreSQL (for auth/admin tables) configured via `DATABASE_URL`
- Sanity project credentials (public dataset works without a token, private datasets require `SANITY_TOKEN`)

## Environment Variables

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | (Optional) Connection string for the primary database. Needed only if you plan to use the auth/admin endpoints. |
| `SANITY_PROJECT_ID` | Sanity project id (defaults to `4bbukn54`). |
| `SANITY_DATASET` | Dataset to read from (defaults to `production`). |
| `SANITY_API_VERSION` | Sanity API version (defaults to `2023-05-03`). |
| `SANITY_TOKEN` | Optional token when querying private content. |
| `SANITY_USE_CDN` | Set to `false` to bypass Sanity CDN for draft reads. |

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

The public endpoints are available under `/api/v1/entries`. Example calls:

- `GET /api/v1/entries/` – list all published entries from Sanity.
- `GET /api/v1/entries/{slug}` – fetch a single published entry by slug.

Both routes hydrate the `content_html` field using the Portable Text from Sanity, preserving callouts, ritual steps, and pull quotes introduced in the Studio schema.
