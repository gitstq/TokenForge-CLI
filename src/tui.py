"""
TUI Dashboard module - Terminal-based interactive dashboard for compression visualization.
Uses only standard library (curses-like rendering with ANSI escape codes).
"""

import sys
import time
import math
from typing import Dict, List, Optional


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @classmethod
    def disable(cls):
        """Disable all colors (for non-TTY environments)."""
        for attr_name in ["RESET", "BOLD", "DIM", "UNDERLINE",
                          "BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE",
                          "BRIGHT_RED", "BRIGHT_GREEN", "BRIGHT_YELLOW", "BRIGHT_BLUE",
                          "BRIGHT_MAGENTA", "BRIGHT_CYAN", "BRIGHT_WHITE",
                          "BG_BLACK", "BG_RED", "BG_GREEN", "BG_YELLOW", "BG_BLUE",
                          "BG_MAGENTA", "BG_CYAN", "BG_WHITE"]:
            setattr(cls, attr_name, "")


def _supports_color() -> bool:
    """Check if the terminal supports color output."""
    if not sys.stdout.isatty():
        return False
    # Check NO_COLOR environment variable
    if os.environ.get("NO_COLOR"):
        return False
    return True


# Disable colors if terminal doesn't support them
try:
    import os
    if not _supports_color():
        Colors.disable()
except Exception:
    Colors.disable()


class TUIRenderer:
    """Terminal UI renderer with box drawing and progress bars."""

    @staticmethod
    def box(title: str, content: List[str], width: int = 60,
            color: str = None) -> str:
        """Render a bordered box with title and content."""
        lines = []

        # Top border
        if color:
            lines.append(f"{color}┌{'─' * (width - 2)}┐{Colors.RESET}")
        else:
            lines.append(f"┌{'─' * (width - 2)}┐")

        # Title
        title_text = f" {title} "
        padding = width - 4 - len(title_text)
        left_pad = padding // 2
        right_pad = padding - left_pad
        if color:
            lines.append(f"{color}│{Colors.RESET}{Colors.BOLD}{' ' * left_pad}{title_text}{' ' * right_pad}{color}│{Colors.RESET}")
        else:
            lines.append(f"│{' ' * left_pad}{title_text}{' ' * right_pad}│")

        # Separator
        if color:
            lines.append(f"{color}├{'─' * (width - 2)}┤{Colors.RESET}")
        else:
            lines.append(f"├{'─' * (width - 2)}┤")

        # Content
        for line in content:
            line_len = len(line) - len(TUIRenderer._strip_ansi(line))
            padding = width - 4 - line_len
            if padding < 0:
                padding = 0
            if color:
                lines.append(f"{color}│{Colors.RESET} {line}{' ' * padding} {color}│{Colors.RESET}")
            else:
                lines.append(f"│ {line}{' ' * padding} │")

        # Bottom border
        if color:
            lines.append(f"{color}└{'─' * (width - 2)}┘{Colors.RESET}")
        else:
            lines.append(f"└{'─' * (width - 2)}┘")

        return "\n".join(lines)

    @staticmethod
    def progress_bar(value: float, max_value: float = 100, width: int = 40,
                     filled_char: str = "█", empty_char: str = "░",
                     color: str = None) -> str:
        """Render a progress bar."""
        if max_value == 0:
            ratio = 0
        else:
            ratio = min(1.0, value / max_value)

        filled = int(width * ratio)
        empty = width - filled

        bar = filled_char * filled + empty_char * empty
        percentage = ratio * 100

        if color:
            return f"{color}{bar}{Colors.RESET} {percentage:.1f}%"
        return f"{bar} {percentage:.1f}%"

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Strip ANSI escape codes from text."""
        import re
        return re.sub(r"\033\[[0-9;]*m", "", text)

    @staticmethod
    def table(headers: List[str], rows: List[List[str]], padding: int = 2) -> str:
        """Render a simple table."""
        if not headers or not rows:
            return ""

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    cell_len = len(TUIRenderer._strip_ansi(str(cell)))
                    col_widths[i] = max(col_widths[i], cell_len)

        lines = []

        # Header
        header_line = ""
        for i, h in enumerate(headers):
            header_line += f"{Colors.BOLD}{h}{Colors.RESET}{' ' * (col_widths[i] - len(h) + padding)}"
        lines.append(header_line)

        # Separator
        sep_line = ""
        for w in col_widths:
            sep_line += "─" * (w + padding)
        lines.append(sep_line)

        # Rows
        for row in rows:
            row_line = ""
            for i, cell in enumerate(row):
                cell_str = str(cell)
                cell_len = len(TUIRenderer._strip_ansi(cell_str))
                row_line += f"{cell_str}{' ' * (col_widths[i] - cell_len + padding)}"
            lines.append(row_line)

        return "\n".join(lines)


class Dashboard:
    """Interactive TUI dashboard for displaying compression results."""

    def __init__(self):
        self.renderer = TUIRenderer()

    def render_compression_report(self, data: Dict) -> str:
        """Render a full compression report dashboard."""
        sections = []

        # Header
        sections.append(self._render_header(data))
        sections.append("")

        # Results overview
        sections.append(self._render_results(data))
        sections.append("")

        # Pipeline visualization
        pipeline = data.get("pipeline", [])
        if pipeline:
            sections.append(self._render_pipeline(pipeline))
            sections.append("")

        # Token savings gauge
        sections.append(self._render_savings_gauge(data))
        sections.append("")

        # Strategy details
        strategy_stats = data.get("strategy_stats", [])
        if strategy_stats:
            sections.append(self._render_strategy_details(strategy_stats))
            sections.append("")

        return "\n".join(sections)

    def _render_header(self, data: Dict) -> str:
        """Render dashboard header."""
        strategies = data.get("strategies_used", [])
        intensity = data.get("intensity", 0)

        content = [
            f"{Colors.BRIGHT_CYAN}TokenSlim-CLI{Colors.RESET} {Colors.DIM}v1.0.0{Colors.RESET}",
            f"{Colors.DIM}Strategies: {', '.join(strategies)}{Colors.RESET}",
            f"{Colors.DIM}Intensity:  {intensity}{Colors.RESET}",
        ]
        return self.renderer.box("Compression Dashboard", content, width=60, color=Colors.CYAN)

    def _render_results(self, data: Dict) -> str:
        """Render results overview box."""
        saved_pct = data.get("token_saved_percent", 0)
        color = Colors.GREEN if saved_pct > 30 else Colors.YELLOW if saved_pct > 15 else Colors.RED

        content = [
            f"Original:     {Colors.BOLD}{data.get('original_chars', 0):,}{Colors.RESET} chars / {Colors.BOLD}{data.get('original_tokens', 0):,}{Colors.RESET} tokens",
            f"Compressed:   {Colors.BOLD}{data.get('compressed_chars', 0):,}{Colors.RESET} chars / {Colors.BOLD}{data.get('compressed_tokens', 0):,}{Colors.RESET} tokens",
            f"Chars Saved:  {color}{data.get('char_saved_percent', 0)}%{Colors.RESET}",
            f"Tokens Saved: {color}{data.get('token_saved_percent', 0)}%{Colors.RESET}",
            f"Ratio:        {data.get('token_ratio', 0)}",
        ]
        return self.renderer.box("Results", content, width=60, color=color)

    def _render_pipeline(self, pipeline: List[Dict]) -> str:
        """Render compression pipeline visualization."""
        content = []
        for i, step in enumerate(pipeline):
            saved = step.get("saved_chars", 0)
            pct = (saved / step["input_chars"] * 100) if step["input_chars"] > 0 else 0

            bar_color = Colors.GREEN if pct > 20 else Colors.YELLOW if pct > 5 else Colors.DIM
            bar = self.renderer.progress_bar(pct, 100, width=20, color=bar_color)

            content.append(
                f"{Colors.BOLD}{i+1}.{Colors.RESET} {step['strategy']:<20} {bar}"
            )

        return self.renderer.box("Pipeline", content, width=60, color=Colors.BLUE)

    def _render_savings_gauge(self, data: Dict) -> str:
        """Render a visual savings gauge."""
        saved_pct = data.get("token_saved_percent", 0)

        # Determine gauge color based on savings
        if saved_pct >= 50:
            gauge_color = Colors.BRIGHT_GREEN
            label = "Excellent"
        elif saved_pct >= 30:
            gauge_color = Colors.GREEN
            label = "Good"
        elif saved_pct >= 15:
            gauge_color = Colors.YELLOW
            label = "Moderate"
        else:
            gauge_color = Colors.RED
            label = "Low"

        # Create a simple gauge visualization
        gauge_width = 40
        filled = int(gauge_width * saved_pct / 100)
        empty = gauge_width - filled

        gauge_line = f"{gauge_color}{'█' * filled}{'░' * empty}{Colors.RESET}"

        content = [
            f"{gauge_line}",
            f"{Colors.BOLD}{saved_pct}%{Colors.RESET} Token Reduction — {gauge_color}{label}{Colors.RESET}",
        ]
        return self.renderer.box("Savings Gauge", content, width=60, color=gauge_color)

    def _render_strategy_details(self, stats: List[Dict]) -> str:
        """Render detailed strategy statistics."""
        content = []
        for stat in stats:
            name = stat.get("strategy", "unknown")
            saved = stat.get("saved_percent", 0)
            color = Colors.GREEN if saved > 20 else Colors.YELLOW if saved > 5 else Colors.DIM

            content.append(f"{color}●{Colors.RESET} {name:<22} {saved}% saved")

        return self.renderer.box("Strategy Details", content, width=60, color=Colors.MAGENTA)

    def render_batch_summary(self, results: List[Dict]) -> str:
        """Render a summary of batch compression results."""
        if not results:
            return f"{Colors.DIM}No results to display.{Colors.RESET}"

        total_original = sum(r.get("original_tokens", 0) for r in results)
        total_compressed = sum(r.get("compressed_tokens", 0) for r in results)
        total_saved_pct = round((1 - total_compressed / total_original) * 100, 1) if total_original > 0 else 0

        content = [
            f"Files Processed: {Colors.BOLD}{len(results)}{Colors.RESET}",
            f"Total Original:   {Colors.BOLD}{total_original:,}{Colors.RESET} tokens",
            f"Total Compressed: {Colors.BOLD}{total_compressed:,}{Colors.RESET} tokens",
            f"Total Saved:      {Colors.GREEN}{total_saved_pct}%{Colors.RESET}",
        ]

        return self.renderer.box("Batch Summary", content, width=60, color=Colors.CYAN)

    def render_strategies_list(self, strategies: List[Dict]) -> str:
        """Render available strategies list."""
        content = []
        for s in strategies:
            content.append(f"{Colors.BOLD}{s['name']:<22}{Colors.RESET} {Colors.DIM}{s['category']}{Colors.RESET}")
            content.append(f"  {s['description']}")

        return self.renderer.box("Available Strategies", content, width=70, color=Colors.BLUE)

    def render_token_estimate(self, estimate_data: Dict) -> str:
        """Render token estimation details."""
        content = [
            f"Total Tokens: {Colors.BOLD}{estimate_data.get('total_tokens', 0):,}{Colors.RESET}",
            f"Total Chars:  {Colors.BOLD}{estimate_data.get('total_chars', 0):,}{Colors.RESET}",
            f"Primary Lang: {Colors.BOLD}{estimate_data.get('primary_language', 'unknown').upper()}{Colors.RESET}",
        ]

        breakdown = estimate_data.get("breakdown", {})
        if breakdown:
            content.append("")
            for lang, info in breakdown.items():
                pct = info.get("proportion", 0)
                tokens = info.get("tokens", 0)
                bar = self.renderer.progress_bar(pct, 100, width=15, color=Colors.CYAN)
                content.append(f"  {lang.upper():<6} {bar} {tokens:,} tokens")

        return self.renderer.box("Token Estimation", content, width=60, color=Colors.GREEN)
