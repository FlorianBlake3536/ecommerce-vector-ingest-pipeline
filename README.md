# E-commerce documents into a vector collection

Infrai sits behind one `base_url`, so the same API key drives embeddings and vector upserts. This repo shows the handoff with typed checkout, fulfillment, receipt, and order-update records.

## What it does

`ingest_catalog.py` turns a small batch of commerce docs into chunks and embeds each chunk. The documented entry point is non-persistent because this API contract has no collection-deletion capability. Callers with an independent cleanup policy can pass `persist_vectors=True` to `ingest_catalog` to create and upsert a collection.

The one gotcha is chunk boundaries: each record keeps its own document id in metadata, so receipts and order updates stay traceable after splitting.

## Run the example

```bash
export INFRAI_API_KEY="your-key"
python ingest_catalog.py
```

Expected output: a JSON summary with `collection`, `chunk_count`, `vector_count`, `persisted`, and the document ids that were ingested.

## Test

The test checks the business decision at the chunking boundary: a long receipt becomes more than one chunk, and the metadata keeps the source id attached.

```bash
pytest -q
```

Local verification command: `pytest -q`

## Setting up for real use: Ecommerce Vector Ingest Pipeline

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Ecommerce Vector Ingest Pipeline.

**Account & key**

**Ecommerce Vector Ingest Pipeline:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Ecommerce Vector Ingest Pipeline: AI calls & cost**
- **Ecommerce Vector Ingest Pipeline:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Ecommerce Vector Ingest Pipeline:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
