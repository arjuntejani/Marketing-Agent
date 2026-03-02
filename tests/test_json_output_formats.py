import json
import tempfile
import unittest
from pathlib import Path

from BrandBrainAI.analytics.pricing_analysis import analyze_pricing
from BrandBrainAI.analytics.text_analysis import analyze_text


class TestJsonOutputFormats(unittest.TestCase):
    def test_pricing_analysis_output_format(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            in_file = td_path / "raw_products.json"
            out_file = td_path / "pricing_analysis.json"

            in_file.write_text(
                json.dumps(
                    {
                        "products": [
                            {"variants": [{"price": "10.00", "compare_at_price": "20.00"}]},
                            {"variants": [{"price": "30.00", "compare_at_price": "30.00"}]},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            self.assertTrue(analyze_pricing(input_path=in_file, output_path=out_file))
            data = json.loads(out_file.read_text(encoding="utf-8"))

            self.assertIn("average_price", data)
            self.assertIn("average_discount_percent", data)
            self.assertIn("price_range", data)
            self.assertIn("product_count", data)
            self.assertIn("priced_variant_count", data)
            self.assertIn("min", data["price_range"])
            self.assertIn("max", data["price_range"])

    def test_text_analysis_output_format(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            raw_text = td_path / "raw_text.txt"
            raw_products = td_path / "raw_products.json"
            out_file = td_path / "text_metrics.json"

            raw_text.write_text("Amazing quality. Shop now.", encoding="utf-8")
            raw_products.write_text(
                json.dumps({"products": [{"title": "Premium Set", "body_html": "Feel confident and buy now"}]}),
                encoding="utf-8",
            )

            self.assertTrue(
                analyze_text(raw_text_path=raw_text, raw_products_path=raw_products, output_path=out_file)
            )
            data = json.loads(out_file.read_text(encoding="utf-8"))

            self.assertIn("word_counts", data)
            self.assertIn("cta_frequency", data)
            self.assertIn("emotional_word_ratio", data)
            self.assertIn("homepage", data["word_counts"])
            self.assertIn("product_descriptions", data["word_counts"])
            self.assertIn("total", data["word_counts"])
            self.assertIn("count", data["cta_frequency"])
            self.assertIn("ratio", data["cta_frequency"])


if __name__ == "__main__":
    unittest.main()
