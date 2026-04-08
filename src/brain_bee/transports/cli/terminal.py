import sys
import readline  # 修复 CJK 字符在终端回退时的残影问题
from datetime import datetime

from brain_bee.runtime.transport_base import Transport
from brain_bee.transports.cli._rich_renderer import (
    SpinnerHandle,
    render_confirm,
    render_markdown,
    render_tool_action,
)


class TerminalTransport(Transport):
    """CLI implementation of the Transport protocol."""

    def __init__(self):
        self._is_streaming = False
        self._current_role = None
        self._stream_buffer: list[str] = []
        self._spinner: SpinnerHandle | None = None

    def _stop_spinner(self) -> None:
        if self._spinner is not None:
            self._spinner.stop()
            self._spinner = None

    def send(self, message: str, role: str = "assistant") -> None:
        """Prints the message to the console with themed role indicator."""
        if self._is_streaming:
            print()
            self._is_streaming = False
        self._stop_spinner()

        timestamp = f"\033[90m[{datetime.now().strftime('%H:%M:%S')}]\033[0m"
        prefix = "🐝 " if role.lower() != "user" else ""
        # 使用黄色高亮角色名
        role_label = f"\033[1;33m{role.upper()}\033[0m"
        print(f"\n{timestamp} {prefix}{role_label} >")
        render_markdown(message)

    def stream_send(self, chunk: str, role: str = "assistant") -> None:
        """Sends a themed message chunk to the console."""
        if not self._is_streaming or self._current_role != role:
            if self._is_streaming:
                if self._stream_buffer:
                    render_markdown("".join(self._stream_buffer))
                self._stream_buffer = []
            self._stop_spinner()

            timestamp = f"\033[90m[{datetime.now().strftime('%H:%M:%S')}]\033[0m"
            prefix = "🐝 " if role.lower() != "user" else ""
            role_label = f"\033[1;33m{role.upper()}\033[0m"
            sys.stdout.write(f"\n{timestamp} {prefix}{role_label} > ")
            self._is_streaming = True
            self._current_role = role

        self._stream_buffer.append(chunk)
        sys.stdout.write(chunk)
        sys.stdout.flush()

    def end_stream(self) -> None:
        """Flush any buffered stream content with Markdown rendering."""
        if self._is_streaming and self._stream_buffer:
            print()
            render_markdown("".join(self._stream_buffer))
            self._stream_buffer = []
            self._is_streaming = False

    def receive(self, prompt: str | None = None) -> str:
        """Receives input with a stylized USER prompt."""
        if self._is_streaming:
            if self._stream_buffer:
                print()
                render_markdown("".join(self._stream_buffer))
                self._stream_buffer = []
            else:
                print()
            self._is_streaming = False
        self._stop_spinner()

        # 默认使用高亮的 USER > 
        if prompt is None:
            prompt = "\033[1;36mUSER >\033[0m "
        
        return input(f"\n{prompt}")

    def confirm_action(self, emoji: str, reason: str, details: str) -> bool:
        """Requests explicit human approval for a high-risk action in the terminal.

        Args:
            emoji: Visual risk indicator.
            reason: Explanation of the risk.
            details: The specific data/command being audited.

        Returns:
            bool: True if approved, False otherwise.
        """
        # Close any active stream before confirming action
        if self._is_streaming:
            if self._stream_buffer:
                print()
                render_markdown("".join(self._stream_buffer))
                self._stream_buffer = []
            else:
                print()
            self._is_streaming = False
        self._stop_spinner()

        render_confirm(emoji, reason, details)

        response = (
            input("\n[Brain Bee] \u786e\u8ba4\u6267\u884c\u4e0a\u8ff0\u64cd\u4f5c\u5417? [Y/n]: ")
            .strip()
            .lower()
        )
        return response == "y"

    def report_action(self, emoji: str, action: str, details: str | None = None) -> None:
        """Prints a dimmed status update to the console for real-time visibility.

        Starts a spinner animation for thinking/executing states.

        Args:
            emoji: Visual descriptor.
            action: Short description of the action.
            details: Optional JSON/Text for deep introspection.
        """
        # Close any active stream before reporting action
        if self._is_streaming:
            if self._stream_buffer:
                print()
                render_markdown("".join(self._stream_buffer))
                self._stream_buffer = []
            else:
                print()
            self._is_streaming = False

        self._stop_spinner()

        # Start spinner for thinking state
        if emoji == "🧠":
            self._spinner = SpinnerHandle(f"{emoji} {action}")
            self._spinner.start()
        else:
            render_tool_action(emoji, action, details)
            # Start spinner for tool execution
            if emoji == "🛠️":
                self._spinner = SpinnerHandle("  ⏳ 执行中...")
                self._spinner.start()
