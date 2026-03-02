import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class TestShopifyDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Provide a lightweight requests stub so module import works in limited envs.
        if "requests" not in sys.modules:
            stub = types.ModuleType("requests")

            class RequestException(Exception):
                pass

            stub.RequestException = RequestException
            stub.get = lambda *args, **kwargs: None
            sys.modules["requests"] = stub

        cls.module = importlib.import_module("BrandBrainAI.extractor.shopify_detector")

    def test_returns_true_for_shopify_marker_and_products_json(self):
        home = Mock()
        home.text = '<html><script src="https://cdn.shopify.com/theme.js"></script></html>'

        products = Mock()
        products.status_code = 200
        products.headers = {"Content-Type": "application/json"}
        products.text = '{"products": []}'
        products.json.return_value = {"products": []}

        with patch("BrandBrainAI.extractor.shopify_detector.requests.get", side_effect=[home, products]):
            self.assertTrue(self.module.is_shopify_store("example.com"))

    def test_returns_false_for_non_200_products_json(self):
        home = Mock()
        home.text = "<html>plain site</html>"

        products = Mock()
        products.status_code = 404
        products.headers = {}
        products.text = ""

        with patch("BrandBrainAI.extractor.shopify_detector.requests.get", side_effect=[home, products]):
            self.assertFalse(self.module.is_shopify_store("https://example.com"))


if __name__ == "__main__":
    unittest.main()
