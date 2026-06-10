"""
Token estimator module - Estimate token count for text using character-based heuristics.
Supports English, Chinese, Japanese, Korean, and mixed-language text.
"""

import re
from typing import Dict, List, Tuple


class TokenEstimator:
    """Estimate token count using character-level heuristics for multiple languages."""

    # Approximate characters per token for different languages
    CHARS_PER_TOKEN = {
        "en": 4.0,      # English: ~4 chars per token
        "zh": 1.5,      # Chinese: ~1.5 chars per token
        "ja": 1.5,      # Japanese: ~1.5 chars per token
        "ko": 2.0,      # Korean: ~2 chars per token
        "code": 3.5,    # Code: ~3.5 chars per token
        "mixed": 2.5,   # Mixed: average
    }

    # Unicode ranges for CJK characters
    CJK_RANGES = [
        (0x4E00, 0x9FFF),    # CJK Unified Ideographs
        (0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
        (0xF900, 0xFAFF),    # CJK Compatibility Ideographs
        (0x2F800, 0x2FA1F),  # CJK Compatibility Ideographs Supplement
    ]

    # Japanese-specific ranges
    JP_RANGES = [
        (0x3040, 0x309F),    # Hiragana
        (0x30A0, 0x30FF),    # Katakana
        (0xFF66, 0xFF9F),    # Halfwidth Katakana
    ]

    # Korean-specific ranges
    KO_RANGES = [
        (0xAC00, 0xD7AF),    # Hangul Syllables
        (0x1100, 0x11FF),    # Hangul Jamo
        (0x3130, 0x318F),    # Hangul Compatibility Jamo
    ]

    @classmethod
    def detect_language_profile(cls, text: str) -> Dict[str, float]:
        """Detect the language composition of text and return proportions."""
        if not text:
            return {"en": 1.0}

        total_chars = len(text)
        counts = {"zh": 0, "ja": 0, "ko": 0, "code": 0, "en": 0}

        for char in text:
            code_point = ord(char)

            # Check CJK
            is_cjk = False
            for start, end in cls.CJK_RANGES:
                if start <= code_point <= end:
                    counts["zh"] += 1
                    is_cjk = True
                    break
            if is_cjk:
                continue

            # Check Japanese
            is_jp = False
            for start, end in cls.JP_RANGES:
                if start <= code_point <= end:
                    counts["ja"] += 1
                    is_jp = True
                    break
            if is_jp:
                continue

            # Check Korean
            is_ko = False
            for start, end in cls.KO_RANGES:
                if start <= code_point <= end:
                    counts["ko"] += 1
                    is_ko = True
                    break
            if is_ko:
                continue

            # Check code-like characters
            if char in '{}[]()=<>;:,./\\|!@#$%^&*+-~`\'"':
                counts["code"] += 1
            elif char.isdigit():
                counts["code"] += 1
            elif char.isalpha():
                counts["en"] += 1
            else:
                counts["en"] += 0.5  # Punctuation, whitespace

        # Calculate proportions
        proportions = {}
        for lang, count in counts.items():
            proportions[lang] = count / total_chars if total_chars > 0 else 0

        return proportions

    @classmethod
    def estimate(cls, text: str) -> int:
        """Estimate token count for the given text."""
        if not text:
            return 0

        profile = cls.detect_language_profile(text)
        total_tokens = 0

        for lang, proportion in profile.items():
            if proportion > 0.01:  # Only count significant proportions
                chars_for_lang = int(len(text) * proportion)
                chars_per_token = cls.CHARS_PER_TOKEN.get(lang, cls.CHARS_PER_TOKEN["mixed"])
                total_tokens += int(chars_for_lang / chars_per_token)

        return max(1, total_tokens)

    @classmethod
    def estimate_detailed(cls, text: str) -> Dict:
        """Return detailed token estimation with breakdown by language."""
        profile = cls.detect_language_profile(text)
        total_tokens = 0
        breakdown = {}

        for lang, proportion in profile.items():
            if proportion > 0.01:
                chars_for_lang = int(len(text) * proportion)
                chars_per_token = cls.CHARS_PER_TOKEN.get(lang, cls.CHARS_PER_TOKEN["mixed"])
                tokens = int(chars_for_lang / chars_per_token)
                breakdown[lang] = {
                    "chars": chars_for_lang,
                    "tokens": tokens,
                    "proportion": round(proportion * 100, 1),
                }
                total_tokens += tokens

        return {
            "total_tokens": total_tokens,
            "total_chars": len(text),
            "breakdown": breakdown,
            "primary_language": max(breakdown, key=lambda k: breakdown[k]["tokens"]) if breakdown else "en",
        }

    @classmethod
    def estimate_lines(cls, lines: List[str]) -> List[Dict]:
        """Estimate tokens for each line in a list."""
        return [
            {
                "line_number": i + 1,
                "text": line,
                "chars": len(line),
                "tokens": cls.estimate(line),
            }
            for i, line in enumerate(lines)
        ]

    @classmethod
    def compression_ratio(cls, original: str, compressed: str) -> Dict:
        """Calculate compression statistics between original and compressed text."""
        orig_tokens = cls.estimate(original)
        comp_tokens = cls.estimate(compressed)
        orig_chars = len(original)
        comp_chars = len(compressed)

        if orig_tokens == 0:
            return {"ratio": 0, "saved_tokens": 0, "saved_chars": 0, "saved_percent": 0}

        return {
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "saved_tokens": orig_tokens - comp_tokens,
            "original_chars": orig_chars,
            "compressed_chars": comp_chars,
            "saved_chars": orig_chars - comp_chars,
            "ratio": round(comp_tokens / orig_tokens, 3),
            "saved_percent": round((1 - comp_tokens / orig_tokens) * 100, 1),
        }
