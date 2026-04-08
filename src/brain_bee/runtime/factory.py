"""
AgentFactory — 数据驱动的 Agent 创建（架构演示版）

实际产品的工厂方法负责：
- 从 manifests/roles/*.md 加载角色 YAML frontmatter
- 根据 allowed_tools 白名单过滤全局工具集
- 隐式注入角色特有工具（Worker 的 report_completed 等）
- 注入执行参数（max_iterations、timeout_seconds、max_replan_count）
- 通过 AgentConfig Pydantic 模型验证参数范围
"""

import logging
from typing import Any

from brain_bee.runtime.agent import BaseAgent
from brain_bee.runtime.guardrails import Guardrails

logger = logging.getLogger(__name__)

# 角色默认执行参数（实际产品从 manifest frontmatter 读取）
ROLE_DEFAULTS: dict[str, dict[str, Any]] = {
    "queen": {"max_iterations": None, "timeout_seconds": None},
    "orchestrator": {"max_replan_count": 3},
    "worker": {"max_iterations": 5, "timeout_seconds": 120},
}


class AgentFactory:
    """根据角色名 + 配置创建 BaseAgent 实例。

    设计原则：所有角色共享 BaseAgent 引擎，差异化通过配置注入。
    不建子类（无 WorkerAgent / OrchestratorAgent），避免抽象膨胀。
    """

    @staticmethod
    def create(role: str = "queen", **kwargs: Any) -> BaseAgent:
        """创建指定角色的 Agent 实例。

        实际产品流程：
        1. 从 manifests/roles/{role}.md 解析 YAML frontmatter
        2. 构建 AgentConfig（frontmatter > ROLE_DEFAULTS > None）
        3. 过滤 allowed_tools 白名单
        4. 注入 Guardrails + EventBus + TokenBudget
        """
        from brain_bee.harness.config import AgentConfig

        defaults = ROLE_DEFAULTS.get(role, {})
        config = AgentConfig(name=role, type=role)

        safety_gate = Guardrails()
        agent = BaseAgent(config=config, safety_gate=safety_gate)

        logger.info(f"Created agent: role={role}")
        return agent
