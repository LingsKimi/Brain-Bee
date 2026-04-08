"""Rich-based terminal renderer with graceful fallback to plain ANSI.

All rendering functions are pure (no side-effects beyond stdout).
Each function imports Rich lazily and falls back to plain ``print()`` when
Rich is not installed.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime

# ---------------------------------------------------------------------------
# Capability detection (module-level, evaluated once)
# ---------------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.status import Status
    from rich.syntax import Syntax
    from rich.text import Text

    _RICH_AVAILABLE = True
    _console = Console()
except ImportError:  # pragma: no cover – fallback path
    _RICH_AVAILABLE = False
    _console = None  # type: ignore[assignment]
    Console = None  # type: ignore[assignment, misc]
    Markdown = None  # type: ignore[assignment, misc]
    Panel = None  # type: ignore[assignment, misc]
    Status = None  # type: ignore[assignment, misc]
    Syntax = None  # type: ignore[assignment, misc]
    Text = None  # type: ignore[assignment, misc]


def _terminal_width() -> int:
    """Return terminal width, clamped to a sane range."""
    return max(60, min(shutil.get_terminal_size().columns, 120))


# ---------------------------------------------------------------------------
# Public rendering API
# ---------------------------------------------------------------------------


def render_markdown(text: str, *, code_theme: str = "monokai") -> None:
    """Render *text* as Rich Markdown with syntax-highlighted code blocks."""
    if _RICH_AVAILABLE and _console is not None and Markdown is not None:
        _console.print(Markdown(text, code_theme=code_theme))
    else:
        print(text)


def render_code(code: str, language: str = "python", *, theme: str = "monokai") -> None:
    """Render standalone code with syntax highlighting."""
    if _RICH_AVAILABLE and _console is not None and Syntax is not None:
        syntax = Syntax(code, language, theme=theme, line_numbers=True)
        _console.print(syntax)
    else:
        print(code)


def render_tool_action(emoji: str, action: str, details: str | None = None) -> None:
    """Render a tool action with Panel for structured params or compact status."""
    ts = datetime.now().strftime("%H:%M:%S")

    if _RICH_AVAILABLE and _console is not None:
        if details:
            _render_tool_panel(emoji, action, details, ts)
        else:
            _render_status_line(emoji, action, ts)
    else:
        dim = "\033[90m"
        cyan = "\033[36m"
        reset = "\033[0m"
        line = f"  {dim}[{ts}]{reset}  {emoji} {cyan}{action}{reset}"
        if details:
            line += f" {dim}({details}){reset}"
        print(line)


def _render_tool_panel(emoji: str, action: str, details: str, ts: str) -> None:
    """Render tool call with parameters in a Rich Panel."""
    body = Text()
    body.append(action, style="bold")
    try:
        parsed = json.loads(details)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        if len(formatted) > 300:
            formatted = formatted[:300] + "…"
    except (json.JSONDecodeError, TypeError):
        formatted = details
    body.append(f"\n\n{formatted}", style="dim")
    panel = Panel(
        body,
        title=f"{emoji} [{ts}]",
        title_align="left",
        border_style="blue",
        width=_terminal_width(),
        padding=(0, 1),
    )
    _console.print(panel)  # type: ignore[union-attr]


def _render_status_line(emoji: str, action: str, ts: str) -> None:
    """Render a compact status line with color coding."""
    if emoji == "✅":
        style = "green"
    elif emoji == "❌":
        style = "red"
    elif emoji == "⚠️":
        style = "yellow"
    else:
        style = "cyan"
    parts = Text()
    parts.append(f"[{ts}]  ", style="dim")
    parts.append(f"{emoji} {action}", style=style)
    _console.print(parts)  # type: ignore[union-attr]


def render_confirm(emoji: str, reason: str, details: str) -> None:
    """Render a high-risk action confirmation prompt."""
    if _RICH_AVAILABLE and _console is not None and Panel is not None:
        body = Text()
        body.append(f"{emoji}  {reason}\n\n", style="bold")
        body.append(details, style="dim")
        panel = Panel(
            body, border_style="red", title="Confirmation Required", width=_terminal_width()
        )
        _console.print(panel)
    else:
        print(f"\n{'!' * 40}")
        print(f"{emoji}  {reason}")
        print(f"\u8be6\u60c5: {details}")
        print(f"{'!' * 40}")


def render_error(message: str) -> None:
    """Render an error message in red."""
    if _RICH_AVAILABLE and _console is not None:
        _console.print(f"[bold red]Error:[/bold red] {message}")
    else:
        print(f"\033[31mError:\033[0m {message}")


def render_warning(message: str) -> None:
    """Render a warning message in yellow."""
    if _RICH_AVAILABLE and _console is not None:
        _console.print(f"[bold yellow]Warning:[/bold yellow] {message}")
    else:
        print(f"\033[33mWarning:\033[0m {message}")


def render_welcome(version: str) -> None:
    """Render the startup welcome banner."""
    if _RICH_AVAILABLE and _console is not None:
        banner = Text()
        banner.append("Brain Bee", style="bold yellow")
        banner.append(f" v{version}", style="dim")
        banner.append(" — \u8702\u7fa4\u667a\u80fd\u4f53", style="italic")
        _console.print(banner)
        _console.rule(style="yellow dim")
    else:
        print(f"\033[33mBrain Bee\033[0m v{version} — \u8702\u7fa4\u667a\u80fd\u4f53")
        print("-" * 40)


class SpinnerHandle:
    """Manages a Rich Status spinner with graceful fallback."""

    def __init__(self, message: str) -> None:
        self._message = message
        self._status: Status | None = None

    def start(self) -> None:
        if _RICH_AVAILABLE and _console is not None and Status is not None:
            self._status = Status(
                self._message,
                spinner="dots",
                console=_console,
            )
            self._status.start()

    def stop(self) -> None:
        if self._status is not None:
            self._status.stop()
            self._status = None
