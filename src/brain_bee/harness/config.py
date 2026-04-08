"""
统一配置模块（架构演示版）

展示数据驱动的配置加载设计：
- Pydantic Settings 模型（环境变量 + .env + 默认值三级优先）
- YAML frontmatter 解析（角色 manifest）
- 角色执行参数验证（AgentConfig field_validator）

实际产品包含更多配置项（日志、MCP、记忆、搜索后端等）。
"""

import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)

load_dotenv(override=True)


# ── Agent 配置 ──────────────────────────────────────────────────

class AgentConfig(BaseModel):
    """Agent 实例配置，从 manifest frontmatter 动态注入。"""
    name: str = "queen"
    type: str = "queen"
    description: str = ""

    # 执行参数
    allowed_tools: list[str] | None = None
    max_iterations: int | None = None
    timeout_seconds: float | None = None
    max_replan_count: int | None = None

    @field_validator("max_iterations")
    @classmethod
    def validate_max_iterations(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 10):
            raise ValueError("max_iterations must be in [1, 10]")
        return v

    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout(cls, v: float | None) -> float | None:
        if v is not None and (v <= 0 or v > 600):
            raise ValueError("timeout_seconds must be in (0, 600]")
        return v


ROLE_DEFAULTS: dict[str, dict[str, Any]] = {
    "queen": {"max_iterations": None, "timeout_seconds": None},
    "orchestrator": {"max_replan_count": 3},
    "worker": {"max_iterations": 5, "timeout_seconds": 120},
}


# ── 全局设置 ────────────────────────────────────────────────────

class Settings(BaseModel):
    """全局配置，从环境变量加载。"""
    model_config = ConfigDict(env_prefix="BRAIN_BEE_")
    
    workspace_root: Path = Field(default_factory=lambda: Path.cwd())
