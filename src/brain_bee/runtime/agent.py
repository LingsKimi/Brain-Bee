"""
BaseAgent — OODA 循环引擎（架构演示版）

本文件展示 Agent 核心的 OODA（观察-判断-决策-行动）循环设计。
实际产品的 LLM 调用、工具执行、多 Agent 编排等逻辑未包含在此演示版中。

设计要点：
  - Agent 完全无状态，所有行为通过 AgentConfig 数据驱动注入
  - 通过 Transport ABC 解耦 I/O，支持 CLI / Web / Worker 等多种传输方式
  - Guardrails 三级安全审计（ALLOW / CONFIRM / BLOCK）保护工具调用
"""

import logging
from typing import Any

from brain_bee.harness.config import AgentConfig
from brain_bee.runtime.guardrails import Guardrails
from brain_bee.runtime.transport_base import Transport

logger = logging.getLogger(__name__)


class BaseAgent:
    """OODA 循环驱动的自主智能体基类。

    核心设计：
      1. Observe  — 通过 Transport 接收用户输入
      2. Orient   — 分类意图（CHAT / TASK），决定是否加载工具
      3. Decide   — 调用 LLM 生成回复或工具调用
      4. Act      — 执行工具并通过 Transport 返回结果

    实际产品中，Decide 阶段会调用 LLM API 并解析 tool_calls，
    Act 阶段会通过 Registry 执行注册的工具。此处仅展示架构。
    """

    def __init__(
        self,
        config: AgentConfig,
        safety_gate: Guardrails | None = None,
    ):
        self.config = config
        self.safety_gate = safety_gate or Guardrails()
        self.messages: list[dict[str, Any]] = []
        self._failure_counter = 0

    def run(self, transport: Transport) -> None:
        """主循环：从 Transport 接收输入，处理后返回响应。

        实际产品中，这是一个完整的 OODA 循环：
        - receive() 阻塞等待用户输入
        - _execute_cycle() 执行多轮 LLM 调用 + 工具执行
        - 支持流式输出（stream_send）和安全审计（confirm_action）
        """
        transport.send(
            f"Brain Bee v1.0 — {self.config.name} 已就绪。输入消息开始对话。"
        )

        while True:
            user_input = transport.receive()
            if user_input.strip().lower() in {"exit", "quit", "q"}:
                transport.send("再见！")
                break

            # Demo: 模拟 OODA 循环的各阶段
            transport.report_action("🧠", "正在分析意图...")

            # Orient: 意图分类（实际产品由 IntentClassifier 完成）
            intent = self._classify_intent(user_input)
            transport.report_action("🔍", f"意图分类: {intent}")

            if intent == "CHAT":
                # 简单聊天 — 跳过工具注入，直接回复
                transport.report_action("✅", "快路径：纯聊天")
                transport.send(f"[Demo] 收到您的消息：{user_input}\n"
                               f"（实际产品会调用 LLM 生成回复）")
            else:
                # 任务处理 — 需要工具调用
                transport.report_action("🛠️", "加载工具定义...")
                self._execute_cycle_demo(transport, user_input, intent)

    def _classify_intent(self, text: str) -> str:
        """意图分类（对齐 Apis 架构）：区分快/慢路径。"""
        text = text.lower()
        
        # 复杂任务关键词：涉及系统构建、大批量修改、深入研究、文档生成
        complex_keywords = ["架构", "开发", "分析", "报告", "生成", "创建项目", "重构", "全量分析", "初始化", "build", "调研", "调查", "总结", "research"]
        if any(kw in text for kw in complex_keywords):
            return "TASK_COMPLEX"
            
        # 简单任务关键词：工具调用（单步可完成）
        simple_keywords = ["查", "搜索", "寻找", "读取", "写入", "执行", "运行", "天气", "search", "删除", "delete", "rm"]
        if any(kw in text for kw in simple_keywords):
            return "TASK_SIMPLE"
            
        return "CHAT"

    def _execute_cycle_demo(self, transport: Transport, user_input: str, intent: str) -> None:
        """演示版多步 OODA 循环模拟（支持快慢分离）。"""
        import time

        # 1. 模拟安全审计逻辑 (Guardrails)
        transport.report_action("🛡️", "正在进行安全审计 (Guardrails)...")
        time.sleep(0.5)

        # 触发模拟安全确认（针对高危动作）
        if any(kw in user_input.lower() for kw in ["删除", "delete", "rm", "清空"]):
            confirmed = transport.confirm_action(
                "🚨", 
                "检测到高危系统变更操作", 
                f"操作目标: {user_input}\n风险等级: HIGH"
            )
            if not confirmed:
                transport.report_action("❌", "用户拒绝执行。")
                transport.send("操作已取消。安全审计拦截了此高危请求。")
                return
            transport.report_action("✅", "用户已授权。")

        # 2. 路径分发：SIMPLE vs COMPLEX
        if intent == "TASK_SIMPLE":
            # ── [快路径：Queen 独立处理] ──
            transport.report_action("🧠", "Queen 识别为简单工具请求 (快路径)")
            time.sleep(0.5)
            
            # 模拟常用工具调用
            tool_name = "web_search" if "天气" in user_input or "搜索" in user_input else "file_io"
            transport.report_action("🛠️", f"调用工具: {tool_name}", '{"query": "' + user_input + '"}')
            time.sleep(1.2)
            
            transport.report_action("✅", "工具返回结果成功 (L1 响应)")
            transport.send(f"已为您完成查询：**{user_input}**。根据工具返回的结果显示，操作已成功执行。", role="queen")
            
        else:
            # ── [慢路径：多 Agent 协作] ──
            transport.report_action("🧠", "意图分析：任务复杂度超出 Queen 处理范围 (慢路径)")
            time.sleep(0.5)
            transport.send("蜂王 (Queen) 识别到复杂工程/调研任务，正在移交给后台 **Orchestrator** 编排引擎...", role="queen")
            time.sleep(1.2)

            transport.report_action("📋", "Orchestrator 正在规划任务清单 (DAG)...")
            time.sleep(1.0)
            
            dag_demo = (
                "### 任务执行计划 (DAG)\n\n"
                "1. **[Worker: 研究/调研]** 深入扫描相关目录、文档及外部资料\n"
                "2. **[Worker: 编码/实验]** 执行原型验证或逻辑修改\n"
                "3. **[Worker: 总结/验证]** 汇整调研报告并运行回归测试"
            )
            transport.send(dag_demo, role="orchestrator")
            time.sleep(1.0)

            # 模拟 Worker 串行执行
            steps = [
                ("🔍", "Worker-1: 发现系统组件...", '{"path": "./src"}'),
                ("🛠️", "Worker-2: 正在执行逻辑处理...", '{"status": "in_progress"}'),
                ("🧪", "Worker-3: 运行自动化回归测试...", '{"passed": 12}')
            ]

            for emoji, action, details in steps:
                transport.report_action(emoji, action)
                time.sleep(1.2)
                transport.report_action("✔️", f"执行完成: {action}", details)
                time.sleep(0.6)

            transport.report_action("✅", "所有原子任务已完成，正在汇总结果...")
            time.sleep(0.8)
            transport.send(f"### 协作任务成功\n\n已为您完成复杂工程任务：**{user_input}**。\n\n- **执行时长**: 模拟 28s\n- **产出物**: 架构一致性校验通过。", role="assistant")

    # ── "试两次后移交" 机制（设计说明） ──
    #
    # 实际产品中，BaseAgent 内联失败检测逻辑：
    #
    # 1. 失败检测：工具异常 + 软失败关键词匹配
    # 2. 失败分类：
    #    - permission → 权限不足，不计次，直接告知用户
    #    - missing_info → 信息不足，不计次，反问用户
    #    - complexity → 计数 +1，注入 hint，继续尝试
    # 3. 达限移交：_failure_counter >= 2 时，构建 handoff_context，
    #    提交 OrchestratorRunner 进行 DAG 调度
    #
    # 这确保了：简单任务 Queen 快速处理（1-2 次工具调用），
    #          复杂任务自动升级到多 Agent 编排，用户无感知。
