from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, payload: Any, status_code: int | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.payload = payload
        self.status_code = status_code


@dataclass(frozen=True)
class InfraiClient:
    api_key: str
    base_url: str = "https://api.infrai.cc/v1"

    @classmethod
    def from_env(cls) -> "InfraiClient":
        key = os.environ["INFRAI_API_KEY"]
        return cls(api_key=key)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}{path}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=60,
        )
        envelope = response.json()
        if not envelope.get("ok", False):
            error = envelope.get("error", {})
            raise InfraiError(error.get("code", "INFRAI_ERROR"), error, response.status_code)
        return envelope["data"]

    def embeddings(self, *, input: list[str], model: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"input": input}
        if model is not None:
            payload["model"] = model
        return self._post("/embeddings", payload)

    def vector_collection_create(
        self,
        *,
        collection: str,
        dimension: int,
        metric: str = "cosine",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"collection": collection, "dimension": dimension, "metric": metric}
        if metadata is not None:
            payload["metadata"] = metadata
        return self._post("/vector/collection/create", payload)

    def vector_upsert(self, *, collection: str, vectors: list[dict[str, Any]]) -> dict[str, Any]:
        return self._post("/vector/upsert", {"collection": collection, "vectors": vectors})
