import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from BrandBrainAI.extractor.product_fetcher import fetch_and_save_products


class FakeResponse:
    def __init__(self, body: str):
        self._body = body.encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestProductFetcher(unittest.TestCase):
    def test_fetch_and_save_products_success(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "raw_products.json"
            with patch(
                "BrandBrainAI.extractor.product_fetcher.urlopen",
                return_value=FakeResponse('{"products": [{"id": 1}]}'),
            ):
                ok = fetch_and_save_products("store.com", output_path=out)

            self.assertTrue(ok)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("products", payload)

    def test_fetch_and_save_products_bad_json(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "raw_products.json"
            with patch(
                "BrandBrainAI.extractor.product_fetcher.urlopen",
                return_value=FakeResponse("not-json"),
            ):
                ok = fetch_and_save_products("store.com", output_path=out)

            self.assertFalse(ok)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
