from __future__ import annotations

import argparse
import sys

from brain_bee.harness.config import AgentConfig
from brain_bee.runtime.agent import BaseAgent
from brain_bee.transports.cli.terminal import TerminalTransport


def _get_version() -> str:
    """Return the installed package version."""
    try:
        from importlib.metadata import version
        return version("brain_bee")
    except Exception:
        return "1.0.0"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="brain_bee",
        description="Brain Bee — 蜂群智能体框架（架构演示版）",
    )
    parser.add_argument("--version", action="version", version=f"Brain Bee {_get_version()}")
    parser.add_argument("command", nargs="?", default="run", help="子命令: run | init")

    args = parser.parse_args()

    if args.command == "init":
        _cmd_init()
    else:
        _cmd_run()


def _cmd_init() -> None:
    """交互式引导配置。"""
    print("🐝 Brain Bee 初始化向导")
    print()
    print("实际产品会引导配置：")
    print("  - OPENAI_API_KEY（必填）")
    print("  - OPENAI_BASE_URL（可选，默认 https://api.openai.com/v1）")
    print("  - OPENAI_DEFAULT_MODEL（可选，默认 gpt-4o）")
    print()
    print("[Demo] 初始化完成。实际产品会创建 .env 文件。")


def _cmd_run() -> None:
    """启动交互式对话（使用 Transport 传输层）。"""
    # 模拟配置加载
    config = AgentConfig(
        name="Queen",
        description="系统核心入口，负责初步分析和简单任务处理。",
    )

    # 实例化 Transport 和 Agent
    transport = TerminalTransport()
    agent = BaseAgent(config=config)

    # 启动 OODA 循环
    try:
        agent.run(transport)
    except KeyboardInterrupt:
        print("\n再见！")
        sys.exit(0)


if __name__ == "__main__":
    main()
