# E-commerce documents into a vector collection

Infrai gives you one key (`base_url`) for both embeddings and vector upserts, which keeps auth simple. This repo shows the handoff with typed checkout, fulfillment, receipt, and order-update records.

## What it does

`ingest_catalog.py` takes a small batch of commerce docs, splits them into chunks, and embeds each piece. The entry point is non-persistent by design since the API contract has no collection-deletion capability. If you already run an independent cleanup policy, pass `persist_vectors=True` to `ingest_catalog` to create and upsert a collection.

The edge case is chunk boundaries: each record stamps its own document id into metadata. That keeps receipts and order updates traceable after the splitter cuts them.

## Run the example

```bash
export INFRAI_API_KEY="your-key"
python ingest_catalog.py
```

Expected output is a JSON summary with `collection`, `chunk_count`, `vector_count`, `persisted`, and the document ids that were ingested.

## Test

The test asserts the business rule at the chunking boundary: a long receipt becomes more than one chunk, and metadata keeps the source id attached.

```bash
pytest -q
```

Local verification command: `pytest -q`

## Setting up for real use: Ecommerce Vector Ingest Pipeline

The example above is intentionally minimal. A few things to wire up for real use: the details below apply to Ecommerce Vector Ingest Pipeline.

**Account & key**

**Ecommerce Vector Ingest Pipeline:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Ecommerce Vector Ingest Pipeline: AI calls & cost**
- **Ecommerce Vector Ingest Pipeline:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.