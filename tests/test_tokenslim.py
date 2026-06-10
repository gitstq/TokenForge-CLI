"""
Unit tests for TokenSlim-CLI compression engine.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_estimator import TokenEstimator
from src.compression import (
    CompressionEngine,
    KeywordExtractionStrategy,
    SemanticDedupStrategy,
    StructuredCompressionStrategy,
    TemplateCompressionStrategy,
    ChunkOptimizationStrategy,
    ChineseOptimizationStrategy,
)
from src.exporter import Exporter


class TestTokenEstimator(unittest.TestCase):
    """Test token estimation."""

    def test_empty_text(self):
        self.assertEqual(TokenEstimator.estimate(""), 0)

    def test_english_text(self):
        text = "Hello world, this is a test of the token estimation system."
        tokens = TokenEstimator.estimate(text)
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, len(text))

    def test_chinese_text(self):
        text = "这是一个测试文本，用于验证中文Token估算的准确性。"
        tokens = TokenEstimator.estimate(text)
        self.assertGreater(tokens, 0)

    def test_mixed_text(self):
        text = "Hello 世界！This is a 混合文本 test."
        tokens = TokenEstimator.estimate(text)
        self.assertGreater(tokens, 0)

    def test_detailed_estimate(self):
        text = "Hello world! This is a test."
        result = TokenEstimator.estimate_detailed(text)
        self.assertIn("total_tokens", result)
        self.assertIn("total_chars", result)
        self.assertIn("breakdown", result)
        self.assertGreater(result["total_tokens"], 0)

    def test_compression_ratio(self):
        original = "This is a longer text that should have more tokens than the compressed version."
        compressed = "Short text."
        result = TokenEstimator.compression_ratio(original, compressed)
        self.assertGreater(result["saved_percent"], 0)
        self.assertLess(result["ratio"], 1.0)

    def test_compression_ratio_empty(self):
        result = TokenEstimator.compression_ratio("", "")
        self.assertEqual(result["ratio"], 0)

    def test_language_detection(self):
        profile = TokenEstimator.detect_language_profile("Hello world")
        self.assertGreater(profile.get("en", 0), 0)

        profile_zh = TokenEstimator.detect_language_profile("你好世界")
        self.assertGreater(profile_zh.get("zh", 0), 0)


class TestKeywordExtraction(unittest.TestCase):
    """Test keyword extraction strategy."""

    def setUp(self):
        self.strategy = KeywordExtractionStrategy()

    def test_empty_text(self):
        compressed, stats = self.strategy.compress("")
        self.assertEqual(compressed, "")

    def test_filler_removal(self):
        text = "It is important to note that this is a test. As a matter of fact, it works well."
        compressed, stats = self.strategy.compress(text)
        self.assertNotIn("It is important to note that", compressed)
        self.assertLess(len(compressed), len(text))

    def test_chinese_filler_removal(self):
        text = "众所周知，这是一个测试。事实上，它运行良好。"
        compressed, stats = self.strategy.compress(text)
        self.assertNotIn("众所周知", compressed)

    def test_stats_structure(self):
        text = "This is a test text for the keyword extraction strategy."
        compressed, stats = self.strategy.compress(text)
        self.assertIn("strategy", stats)
        self.assertIn("original_chars", stats)
        self.assertIn("compressed_chars", stats)


class TestSemanticDedup(unittest.TestCase):
    """Test semantic deduplication strategy."""

    def setUp(self):
        self.strategy = SemanticDedupStrategy()

    def test_empty_text(self):
        compressed, stats = self.strategy.compress("")
        self.assertEqual(compressed, "")

    def test_duplicate_removal(self):
        text = "This is a unique line.\nThis is a unique line.\nAnother unique line."
        compressed, stats = self.strategy.compress(text, intensity=0.8)
        lines = [l.strip() for l in compressed.split("\n") if l.strip()]
        # Should have fewer lines than original
        self.assertLessEqual(len(lines), 2)

    def test_unique_preservation(self):
        text = "First unique line.\nSecond unique line.\nThird unique line."
        compressed, stats = self.strategy.compress(text, intensity=0.3)
        lines = [l.strip() for l in compressed.split("\n") if l.strip()]
        self.assertEqual(len(lines), 3)


class TestStructuredCompression(unittest.TestCase):
    """Test structured content compression."""

    def setUp(self):
        self.strategy = StructuredCompressionStrategy()

    def test_empty_text(self):
        compressed, stats = self.strategy.compress("")
        self.assertEqual(compressed, "")

    def test_code_block_comment_removal(self):
        text = '```python\n# This is a comment\nx = 1\n```'
        compressed, stats = self.strategy.compress(text, intensity=0.5)
        self.assertNotIn("# This is a comment", compressed)


class TestTemplateCompression(unittest.TestCase):
    """Test template compression strategy."""

    def setUp(self):
        self.strategy = TemplateCompressionStrategy()

    def test_empty_text(self):
        compressed, stats = self.strategy.compress("")
        self.assertEqual(compressed, "")

    def test_abbreviation(self):
        text = "Artificial intelligence and machine learning are important."
        compressed, stats = self.strategy.compress(text, intensity=0.5)
        self.assertIn("AI", compressed)

    def test_chinese_abbreviation(self):
        text = "人工智能和机器学习非常重要。"
        compressed, stats = self.strategy.compress(text, intensity=0.9)
        self.assertIn("AI", compressed)


class TestChineseOptimization(unittest.TestCase):
    """Test Chinese text optimization."""

    def setUp(self):
        self.strategy = ChineseOptimizationStrategy()

    def test_empty_text(self):
        compressed, stats = self.strategy.compress("")
        self.assertEqual(compressed, "")

    def test_non_chinese_passthrough(self):
        text = "This is English text."
        compressed, stats = self.strategy.compress(text)
        self.assertEqual(compressed, text)

    def test_chinese_redundancy_removal(self):
        text = "使用使用这个工具来进行分析分析"
        compressed, stats = self.strategy.compress(text, intensity=0.5)
        self.assertLessEqual(len(compressed), len(text))


class TestCompressionEngine(unittest.TestCase):
    """Test the main compression engine."""

    def setUp(self):
        self.engine = CompressionEngine()

    def test_list_strategies(self):
        strategies = self.engine.list_strategies()
        self.assertEqual(len(strategies), 6)

    def test_compress_empty(self):
        compressed, stats = self.engine.compress("")
        self.assertIn("error", stats)

    def test_compress_with_all_strategies(self):
        text = "This is a test. This is also a test. Artificial intelligence is great."
        compressed, stats = self.engine.compress(text)
        self.assertIn("compressed_text", stats)
        self.assertIn("pipeline", stats)
        self.assertLess(len(compressed), len(text))

    def test_compress_specific_strategy(self):
        text = "Artificial intelligence is a field of computer science."
        compressed, stats = self.engine.compress(text, strategies=["template"])
        self.assertEqual(len(stats["strategies_used"]), 1)

    def test_compress_file(self):
        # Create a temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("This is a test file for compression.")
            temp_path = f.name

        try:
            compressed, stats = self.engine.compress_file(temp_path)
            self.assertGreater(len(compressed), 0)
        finally:
            os.unlink(temp_path)

    def test_compress_file_not_found(self):
        compressed, stats = self.engine.compress_file("/nonexistent/file.txt")
        self.assertIn("error", stats)

    def test_invalid_strategy(self):
        with self.assertRaises(ValueError):
            self.engine.get_strategy("nonexistent_strategy")


class TestExporter(unittest.TestCase):
    """Test export functionality."""

    def setUp(self):
        self.sample_data = {
            "strategies_used": ["template", "keyword_extraction"],
            "intensity": 0.5,
            "original_chars": 100,
            "compressed_chars": 70,
            "char_saved_percent": 30.0,
            "original_tokens": 25,
            "compressed_tokens": 18,
            "token_saved_percent": 28.0,
            "token_ratio": 0.72,
            "pipeline": [
                {"strategy": "template", "input_chars": 100, "output_chars": 85, "saved_chars": 15},
                {"strategy": "keyword_extraction", "input_chars": 85, "output_chars": 70, "saved_chars": 15},
            ],
            "original_text": "This is a sample original text for testing export functionality.",
            "compressed_text": "This is sample text for testing export.",
        }

    def test_json_export(self):
        result = Exporter.to_json(self.sample_data)
        import json
        data = json.loads(result)
        self.assertIn("strategies_used", data)

    def test_csv_export(self):
        result = Exporter.to_csv(self.sample_data)
        self.assertIn("Metric", result)
        self.assertIn("Value", result)

    def test_markdown_export(self):
        result = Exporter.to_markdown(self.sample_data)
        self.assertIn("# TokenSlim", result)
        self.assertIn("## Results", result)

    def test_text_export(self):
        result = Exporter.to_text(self.sample_data)
        self.assertIn("TokenSlim", result)

    def test_export_with_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            Exporter.to_json(self.sample_data, output_path=temp_path)
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, "r") as f:
                content = f.read()
            self.assertIn("strategies_used", content)
        finally:
            os.unlink(temp_path)

    def test_unsupported_format(self):
        with self.assertRaises(ValueError):
            Exporter.export(self.sample_data, format="xml")


if __name__ == "__main__":
    unittest.main()
