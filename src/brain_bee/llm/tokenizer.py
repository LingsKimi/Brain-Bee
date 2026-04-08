"""Token counting and JSON validation utilities.

This module provides self-calculated token estimation and JSON integrity
validation, avoiding dependency on API responses which may vary across vendors.
"""

import json
import re
from typing import Any


class Tokenizer:
    """Token estimation utility with vendor-independent calculation."""

    # Chinese character pattern (CJK Unified Ideographs + Extension A)
    CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")

    @staticmethod
    def count_text(text: str) -> int:
        """
        Estimate token count for a single text string.

        Estimation rules (conservative):
        - Chinese: 1 token ≈ 1.5 characters (conservative estimate)
        - English/numbers/symbols: 1 token ≈ 4 characters
        - Mixed: Calculate separately and sum

        Args:
            text: The text string to estimate

        Returns:
            Estimated token count (minimum 1 for non-empty text)
        """
        if not text:
            return 0

        # Count Chinese characters
        chinese_chars = len(Tokenizer.CHINESE_PATTERN.findall(text))

        # Count non-Chinese characters
        non_chinese_chars = len(text) - chinese_chars

        # Calculate tokens (conservative estimation)
        chinese_tokens = int(chinese_chars / 1.5)
        non_chinese_tokens = int(non_chinese_chars / 4)

        return max(1, chinese_tokens + non_chinese_tokens)

    @staticmethod
    def count_messages(messages: list[dict[str, Any]]) -> int:
        """
        Calculate total token count for a message list.

        Args:
            messages: List of messages in OpenAI format

        Returns:
            Total estimated token count
        """
        total = 0
        for msg in messages:
            # Count content
            content = msg.get("content", "")
            if content:
                total += Tokenizer.count_text(content)

            # Count tool_calls
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                for tc in tool_calls:
                    func = tc.get("function", {})
                    name = func.get("name", "")
                    args = func.get("arguments", "")
                    total += Tokenizer.count_text(name)
                    total += Tokenizer.count_text(args)

        return total


def validate_json_arguments(arguments: str) -> bool:
    """
    Validate JSON string integrity for streaming tool call arguments.

    Checks:
    1. Bracket matching ({ } [ ])
    2. JSON parseability (via json.loads)

    Args:
        arguments: The JSON string to validate

    Returns:
        True if JSON is complete and valid, False otherwise
    """
    if not arguments:
        return False

    # Bracket matching check
    stack = []
    for char in arguments:
        if char in "{[":
            stack.append(char)
        elif char in "}]":
            if not stack:
                return False
            if (char == "}" and stack[-1] != "{") or (char == "]" and stack[-1] != "["):
                return False
            stack.pop()

    if stack:  # Unclosed brackets
        return False

    # Parse validation
    try:
        json.loads(arguments)
        return True
    except (json.JSONDecodeError, ValueError, TypeError):
        return False
