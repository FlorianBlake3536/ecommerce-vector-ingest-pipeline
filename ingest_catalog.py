from __future__ import annotations

import json

from catalog_ingest import CommerceDocument, IngestRequest, ingest_catalog
from infrai_client import InfraiClient


if __name__ == "__main__":
    sample = IngestRequest(
        collection="creator-commerce-docs",
        documents=[
            CommerceDocument(
                document_id="order-1001",
                kind="checkout",
                title="Checkout confirmation",
                body="Order 1001 was placed for two print bundles and a monthly membership.",
                customer_id="cust-9",
            ),
            CommerceDocument(
                document_id="order-1001-receipt",
                kind="receipt",
                title="Receipt",
                body="Receipt for order 1001 lists the payment method, tax, and final total.",
                customer_id="cust-9",
            ),
            CommerceDocument(
                document_id="order-1001-fulfillment",
                kind="fulfillment",
                title="Fulfillment update",
                body="The print bundles shipped today. Tracking number and delivery window are included.",
                customer_id="cust-9",
            ),
            CommerceDocument(
                document_id="order-1001-update",
                kind="order_update",
                title="Customer message",
                body="Customer asked to change the delivery address before the package leaves the warehouse.",
                customer_id="cust-9",
            ),
        ],
    )
    result = ingest_catalog(sample, InfraiClient.from_env())
    print(json.dumps(result, indent=2))
