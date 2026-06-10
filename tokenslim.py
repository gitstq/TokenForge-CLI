"""
Main CLI entry point for TokenSlim-CLI.
Zero-dependency terminal LLM token intelligent compression engine.
"""

import sys
import os
import argparse
import json

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import __version__
from src.token_estimator import TokenEstimator
from src.compression import CompressionEngine
from src.exporter import Exporter
from src.tui import Dashboard


def cmd_compress(args):
    """Handle the compress command."""
    engine = CompressionEngine()
    dashboard = Dashboard()

    # Read input
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        # Read from stdin
        text = sys.stdin.read()

    if not text.strip():
        print("Error: No input text provided.", file=sys.stderr)
        sys.exit(1)

    # Parse strategies
    strategies = None
    if args.strategies:
        strategies = [s.strip() for s in args.strategies.split(",")]

    # Compress
    compressed, stats = engine.compress(text, strategies=strategies, intensity=args.intensity)

    # Output
    if args.output:
        Exporter.export(stats, format=args.format, output_path=args.output)
        print(f"Report exported to: {args.output}")
    elif args.format and args.format != "text":
        result = Exporter.export(stats, format=args.format)
        print(result)
    elif args.quiet:
        print(compressed)
    else:
        # Show dashboard
        print(dashboard.render_compression_report(stats))
        print()
        print(f"{Dashboard.renderer.box if hasattr(Dashboard, 'renderer') else ''}")
        print()
        # Show compressed text preview
        preview_len = min(500, len(compressed))
        print(f"{compressed[:preview_len]}{'...' if len(compressed) > preview_len else ''}")


def cmd_estimate(args):
    """Handle the estimate command."""
    dashboard = Dashboard()

    # Read input
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("Error: No input text provided.", file=sys.stderr)
        sys.exit(1)

    if args.detailed:
        estimate = TokenEstimator.estimate_detailed(text)
        print(dashboard.render_token_estimate(estimate))
    else:
        tokens = TokenEstimator.estimate(text)
        print(tokens)


def cmd_strategies(args):
    """Handle the strategies command."""
    engine = CompressionEngine()
    strategies = engine.list_strategies()
    dashboard = Dashboard()

    if args.json:
        print(json.dumps(strategies, indent=2, ensure_ascii=False))
    else:
        print(dashboard.render_strategies_list(strategies))


def cmd_batch(args):
    """Handle the batch compression command."""
    engine = CompressionEngine()
    dashboard = Dashboard()

    if not args.files:
        print("Error: No files specified for batch processing.", file=sys.stderr)
        sys.exit(1)

    results = []
    for file_path in args.files:
        if not os.path.isfile(file_path):
            print(f"Warning: Skipping non-existent file: {file_path}", file=sys.stderr)
            continue

        compressed, stats = engine.compress_file(file_path, intensity=args.intensity)
        stats["file"] = file_path
        results.append(stats)

        if not args.quiet:
            saved = stats.get("token_saved_percent", 0)
            print(f"  {file_path}: {saved}% token reduction")

    if not results:
        print("No files processed.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        Exporter.export({"batch_results": results}, format=args.format, output_path=args.output)
        print(f"\nBatch report exported to: {args.output}")
    else:
        print()
        print(dashboard.render_batch_summary(results))


def cmd_compare(args):
    """Handle the compare command - compare original vs compressed."""
    engine = CompressionEngine()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("Error: No input text provided.", file=sys.stderr)
        sys.exit(1)

    compressed, stats = engine.compress(text, intensity=args.intensity)

    # Side-by-side comparison
    orig_lines = text.split("\n")
    comp_lines = compressed.split("\n")

    max_lines = max(len(orig_lines), len(comp_lines))
    display_lines = min(max_lines, 50)  # Limit display

    print(f"{'─── Original ───':<40} {'─── Compressed ───':<40}")
    print("─" * 80)

    for i in range(display_lines):
        orig = orig_lines[i][:38] if i < len(orig_lines) else ""
        comp = comp_lines[i][:38] if i < len(comp_lines) else ""

        if orig != comp:
            marker = "│"
        else:
            marker = "│"

        print(f"{orig:<39}{marker}{comp}")

    if max_lines > display_lines:
        print(f"\n... ({max_lines - display_lines} more lines)")

    # Summary
    print(f"\n{'─' * 80}")
    print(f"Original: {len(text)} chars / {stats['original_tokens']} tokens")
    print(f"Compressed: {len(compressed)} chars / {stats['compressed_tokens']} tokens")
    print(f"Saved: {stats['token_saved_percent']}%")


def main():
    parser = argparse.ArgumentParser(
        prog="tokenslim",
        description="TokenSlim-CLI - Lightweight Terminal LLM Token Intelligent Compression Engine",
        epilog="Zero Dependencies | Pure Python | 6 Strategies | TUI Dashboard",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # compress command
    compress_parser = subparsers.add_parser("compress", help="Compress text to reduce token usage")
    compress_parser.add_argument("-t", "--text", help="Text to compress")
    compress_parser.add_argument("-f", "--file", help="File to compress")
    compress_parser.add_argument("-s", "--strategies", help="Comma-separated strategy names")
    compress_parser.add_argument("-i", "--intensity", type=float, default=0.5,
                                help="Compression intensity (0.0-1.0, default: 0.5)")
    compress_parser.add_argument("-o", "--output", help="Output file path for report")
    compress_parser.add_argument("--format", choices=["json", "csv", "markdown", "text"],
                                default="text", help="Output format")
    compress_parser.add_argument("-q", "--quiet", action="store_true",
                                help="Output only compressed text")

    # estimate command
    estimate_parser = subparsers.add_parser("estimate", help="Estimate token count for text")
    estimate_parser.add_argument("-t", "--text", help="Text to estimate")
    estimate_parser.add_argument("-f", "--file", help="File to estimate")
    estimate_parser.add_argument("-d", "--detailed", action="store_true",
                                 help="Show detailed breakdown")

    # strategies command
    strategies_parser = subparsers.add_parser("strategies", help="List available compression strategies")
    strategies_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # batch command
    batch_parser = subparsers.add_parser("batch", help="Batch compress multiple files")
    batch_parser.add_argument("files", nargs="+", help="Files to compress")
    batch_parser.add_argument("-i", "--intensity", type=float, default=0.5,
                              help="Compression intensity (0.0-1.0, default: 0.5)")
    batch_parser.add_argument("-o", "--output", help="Output file path for report")
    batch_parser.add_argument("--format", choices=["json", "csv", "markdown", "text"],
                              default="text", help="Output format")
    batch_parser.add_argument("-q", "--quiet", action="store_true", help="Suppress per-file output")

    # compare command
    compare_parser = subparsers.add_parser("compare", help="Compare original vs compressed text")
    compare_parser.add_argument("-t", "--text", help="Text to compress and compare")
    compare_parser.add_argument("-f", "--file", help="File to compress and compare")
    compare_parser.add_argument("-i", "--intensity", type=float, default=0.5,
                                help="Compression intensity (0.0-1.0, default: 0.5)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "compress": cmd_compress,
        "estimate": cmd_estimate,
        "strategies": cmd_strategies,
        "batch": cmd_batch,
        "compare": cmd_compare,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
