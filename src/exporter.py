"""
Export module - Export compression results to multiple formats (JSON, CSV, Markdown).
"""

import json
import csv
import io
import os
from typing import Dict, List, Optional
from datetime import datetime


class Exporter:
    """Export compression results to various formats."""

    @staticmethod
    def to_json(data: Dict, output_path: Optional[str] = None, indent: int = 2) -> str:
        """Export data as JSON string or file."""
        # Prepare serializable data
        serializable = {}
        for key, value in data.items():
            if key in ("original_text", "compressed_text"):
                # Truncate long texts in export
                serializable[key] = value[:500] + "..." if len(value) > 500 else value
            elif isinstance(value, (str, int, float, bool, list, dict)):
                serializable[key] = value
            else:
                serializable[key] = str(value)

        result = json.dumps(serializable, indent=indent, ensure_ascii=False, default=str)

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)

        return result

    @staticmethod
    def to_csv(data: Dict, output_path: Optional[str] = None) -> str:
        """Export compression statistics as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["Metric", "Value"])

        # Basic stats
        rows = [
            ("Strategies Used", ", ".join(data.get("strategies_used", []))),
            ("Intensity", data.get("intensity", 0)),
            ("Original Characters", data.get("original_chars", 0)),
            ("Compressed Characters", data.get("compressed_chars", 0)),
            ("Characters Saved (%)", data.get("char_saved_percent", 0)),
            ("Original Tokens (est.)", data.get("original_tokens", 0)),
            ("Compressed Tokens (est.)", data.get("compressed_tokens", 0)),
            ("Tokens Saved (%)", data.get("token_saved_percent", 0)),
            ("Token Compression Ratio", data.get("token_ratio", 0)),
        ]

        # Pipeline stats
        pipeline = data.get("pipeline", [])
        for step in pipeline:
            rows.append((
                f"  Step: {step['strategy']}",
                f"{step['input_chars']} -> {step['output_chars']} ({step['saved_chars']} saved)"
            ))

        for row in rows:
            writer.writerow(row)

        result = output.getvalue()

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                f.write(result)

        return result

    @staticmethod
    def to_markdown(data: Dict, output_path: Optional[str] = None) -> str:
        """Export compression report as Markdown."""
        lines = []

        lines.append("# TokenSlim Compression Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Overview
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Strategies Used:** {', '.join(data.get('strategies_used', []))}")
        lines.append(f"- **Intensity Level:** {data.get('intensity', 0)}")
        lines.append("")

        # Results
        lines.append("## Results")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Original Characters | {data.get('original_chars', 0)} |")
        lines.append(f"| Compressed Characters | {data.get('compressed_chars', 0)} |")
        lines.append(f"| Characters Saved | {data.get('char_saved_percent', 0)}% |")
        lines.append(f"| Original Tokens (est.) | {data.get('original_tokens', 0)} |")
        lines.append(f"| Compressed Tokens (est.) | {data.get('compressed_tokens', 0)} |")
        lines.append(f"| Tokens Saved | {data.get('token_saved_percent', 0)}% |")
        lines.append(f"| Compression Ratio | {data.get('token_ratio', 0)} |")
        lines.append("")

        # Pipeline
        pipeline = data.get("pipeline", [])
        if pipeline:
            lines.append("## Compression Pipeline")
            lines.append("")
            lines.append("| Step | Strategy | Input | Output | Saved |")
            lines.append("|------|----------|-------|--------|-------|")
            for i, step in enumerate(pipeline, 1):
                lines.append(
                    f"| {i} | {step['strategy']} | {step['input_chars']} | "
                    f"{step['output_chars']} | {step['saved_chars']} |"
                )
            lines.append("")

        # Content preview
        original = data.get("original_text", "")
        compressed = data.get("compressed_text", "")
        if original and compressed:
            lines.append("## Content Preview")
            lines.append("")
            lines.append("### Original (first 300 chars)")
            lines.append("")
            lines.append("```")
            lines.append(original[:300] + ("..." if len(original) > 300 else ""))
            lines.append("```")
            lines.append("")
            lines.append("### Compressed (first 300 chars)")
            lines.append("")
            lines.append("```")
            lines.append(compressed[:300] + ("..." if len(compressed) > 300 else ""))
            lines.append("```")
            lines.append("")

        result = "\n".join(lines)

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)

        return result

    @staticmethod
    def to_text(data: Dict, output_path: Optional[str] = None) -> str:
        """Export as plain text summary."""
        lines = []
        lines.append("=" * 60)
        lines.append("  TokenSlim Compression Report")
        lines.append(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"  Strategies: {', '.join(data.get('strategies_used', []))}")
        lines.append(f"  Intensity:  {data.get('intensity', 0)}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("  RESULTS")
        lines.append("-" * 60)
        lines.append(f"  Original Chars:    {data.get('original_chars', 0)}")
        lines.append(f"  Compressed Chars:  {data.get('compressed_chars', 0)}")
        lines.append(f"  Chars Saved:       {data.get('char_saved_percent', 0)}%")
        lines.append(f"  Original Tokens:   {data.get('original_tokens', 0)}")
        lines.append(f"  Compressed Tokens: {data.get('compressed_tokens', 0)}")
        lines.append(f"  Tokens Saved:      {data.get('token_saved_percent', 0)}%")
        lines.append(f"  Compression Ratio: {data.get('token_ratio', 0)}")
        lines.append("-" * 60)

        result = "\n".join(lines)

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)

        return result

    @classmethod
    def export(cls, data: Dict, format: str = "text", output_path: Optional[str] = None) -> str:
        """Export data in specified format."""
        exporters = {
            "json": cls.to_json,
            "csv": cls.to_csv,
            "markdown": cls.to_markdown,
            "md": cls.to_markdown,
            "text": cls.to_text,
            "txt": cls.to_text,
        }

        exporter = exporters.get(format.lower())
        if not exporter:
            raise ValueError(f"Unsupported format: {format}. Supported: {', '.join(exporters.keys())}")

        return exporter(data, output_path)
