from abc import ABC, abstractmethod


class Transport(ABC):
    """Abstract Base Class for agent communication.

    Ensures Core Agent logic is decoupled from specific I/O implementations
    (CLI, WebSockets, APIs, etc.).
    """

    @abstractmethod
    def send(self, message: str, role: str = "assistant") -> None:
        """Sends a message to the user or interface.

        Args:
            message: The content to transmit.
            role: The role attribute of the sender (e.g., 'assistant', 'system').
        """
        pass

    @abstractmethod
    def stream_send(self, chunk: str, role: str = "assistant") -> None:
        """Sends a message chunk to the user or interface for streaming.

        Args:
            chunk: The text chunk to transmit.
            role: The role attribute of the sender.
        """
        pass

    @abstractmethod
    def receive(self, prompt: str | None = None) -> str:
        """Receives a message from the user or interface.

        Args:
            prompt: Optional text to display before receiving input.

        Returns:
            str: The raw input content.
        """
        pass

    @abstractmethod
    def confirm_action(self, emoji: str, reason: str, details: str) -> bool:
        """Requests explicit human approval for a high-risk action.

        Args:
            emoji: Visual risk indicator.
            reason: Explanation of the risk.
            details: The specific data/command being audited.

        Returns:
            bool: True if approved, False otherwise.
        """
        pass

    @abstractmethod
    def report_action(self, emoji: str, action: str, details: str | None = None) -> None:
        """Logs a process or tool execution to the channel for visibility.

        Args:
            emoji: Visual descriptor (e.g., 🧠, 🛠️, ✅).
            action: Short description of the action.
            details: Optional JSON/Text for deep introspection.
        """
        pass
