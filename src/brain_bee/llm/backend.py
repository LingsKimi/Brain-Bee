"""
LLM Backend 抽象层（架构演示版）

定义 LLM 调用的统一接口。实际产品的 HttpxBackend 实现了：
- OpenAI 兼容 API 调用（支持 Kimi/DeepSeek/等任意兼容供应商）
- SSE 流式响应解析
- Token 计数（中英混合估算 + API usage 优先）
- Embedding 生成（用于 Skill 语义搜索）

此处仅保留 ABC 接口定义和 Mock 实现，供演示架构设计。
"""

from abc import ABC, abstractmethod
from typing import Any


class LLMBackend(ABC):
    """LLM 调用抽象基类。

    设计决策：
      - 使用 ABC 而非 Protocol，因为 LLM 调用是核心依赖，需要显式继承
      - completion() 同时支持流式和非流式，通过 stream 参数控制
      - embed() 为 Skill 语义搜索提供向量能力
    """

    @abstractmethod
    def completion(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """调用 LLM 生成回复。

        Args:
            messages: OpenAI 格式消息列表
            model: 模型 ID（None 使用默认）
            tools: OpenAI 格式工具定义列表
            temperature: 采样温度
            stream: 是否流式返回

        Returns:
            非流式：完整响应对象
            流式：迭代器，逐 token 返回
        """

    @abstractmethod
    def count_tokens(self, messages: list[dict[str, Any]]) -> int:
        """计算消息列表的 token 数。"""

    @abstractmethod
    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """生成文本向量（用于 Skill 语义搜索）。"""


class MockBackend(LLMBackend):
    """演示用 Mock 实现。实际产品使用 HttpxBackend（httpx + SSE）。"""

    def completion(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "[Demo] LLM response would be generated here.",
                },
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
        }

    def count_tokens(self, messages: list[dict[str, Any]]) -> int:
        return sum(len(m.get("content", "").split()) for m in messages)

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        return [[0.0] * 128 for _ in texts]
