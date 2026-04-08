"""
Guardrails — 三级安全审计（架构演示版）

实际产品实现了完整的安全审计系统：
- 基于工具元数据（risk_level、is_read_only）的动态决策
- Conservative / YOLO 双审批模式
- 会话级审批缓存（sha256 签名去重）
- MCP 工具风险推断（从工具名正则推断 risk_level）
"""

import logging
from collections.abc import Callable
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyStatus(str, Enum):
    ALLOW = "ALLOW"      # 自动放行
    CONFIRM = "CONFIRM"  # 需要用户确认
    BLOCK = "BLOCK"      # 硬拦截


class Guardrails:
    """三级阶梯式安全审计。

    决策逻辑：
      1. 查询工具元数据（risk_level / is_read_only）
      2. low + readonly → ALLOW
      3. high → CONFIRM
      4. 静态规则匹配（命令模式、路径模式）
      5. BLOCK 级硬拦截（rm -rf /、特权命令等）

    审批模式：
      - Conservative（默认）：工作区内放行，工作区外首次审批后缓存
      - YOLO：BLOCK 级仍拦截，其余自动放行
    """

    def __init__(
        self,
        approval_mode: str = "conservative",
        metadata_lookup: Callable | None = None,
    ):
        self.approval_mode = approval_mode
        self._metadata_lookup = metadata_lookup
        self._approval_cache: set[str] = set()

    def audit_tool_call(self, tool_name: str, params: dict) -> SafetyStatus:
        """审计工具调用请求。

        实际产品会：
        1. 从 Registry 查询工具的 risk_level 和 is_read_only
        2. 匹配安全策略（security_policies.yaml）
        3. 检查审批缓存
        4. 返回审计结果

        此处为演示版简化实现。
        """
        high_risk_indicators = ["delete", "remove", "rm ", "drop", "format"]
        params_str = str(params).lower()

        for indicator in high_risk_indicators:
            if indicator in params_str:
                logger.warning(f"High-risk operation detected: {tool_name}")
                return SafetyStatus.CONFIRM

        return SafetyStatus.ALLOW

    def confirm_action(self, emoji: str, reason: str, details: str) -> bool:
        """请求用户确认（由 Transport 层实际执行）。"""
        return True  # Demo: 自动确认
