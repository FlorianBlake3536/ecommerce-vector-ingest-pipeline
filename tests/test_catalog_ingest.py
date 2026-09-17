from catalog_ingest import CommerceDocument, chunk_document, build_vectors


def test_long_receipt_splits_and_keeps_source_id():
    document = CommerceDocument(
        document_id="receipt-77",
        kind="receipt",
        title="Receipt",
        body="x" * 800,
        customer_id="cust-77",
    )
    chunks = chunk_document(document, chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    assert {chunk.document_id for chunk in chunks} == {"receipt-77"}
    assert chunks[0].kind == "receipt"


def test_vectors_keep_chunk_metadata():
    document = CommerceDocument(
        document_id="update-12",
        kind="order_update",
        title="Order update",
        body="Customer changed the delivery address.",
        customer_id="cust-12",
    )
    chunks = chunk_document(document, chunk_size=120, chunk_overlap=10)
    vectors = build_vectors(chunks, [[0.1, 0.2, 0.3] for _ in chunks])

    assert vectors[0]["metadata"]["document_id"] == "update-12"
    assert vectors[0]["id"] == "update-12:0"
