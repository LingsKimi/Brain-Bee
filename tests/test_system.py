import pytest
from unittest.mock import MagicMock
from brain_bee.runtime.agent import BaseAgent
from brain_bee.harness.config import AgentConfig
from brain_bee.runtime.transport_base import Transport

class MockTransport(Transport):
    """Mock transport for system testing."""
    def __init__(self, inputs=None):
        self.inputs = inputs or []
        self.sent_messages = []
        self.reported_actions = []
        self.confirmed = True

    def send(self, message: str, role: str = "assistant"):
        self.sent_messages.append((role, message))

    def stream_send(self, chunk: str, role: str = "assistant"):
        pass

    def receive(self, prompt: str | None = None) -> str:
        if not self.inputs:
            return "exit"
        return self.inputs.pop(0)

    def confirm_action(self, emoji: str, reason: str, details: str) -> bool:
        return self.confirmed

    def report_action(self, emoji: str, action: str, details: str | None = None):
        self.reported_actions.append((emoji, action, details))

def test_agent_intent_classification():
    """Test that the agent correctly distinguishes between CHAT, TASK_SIMPLE, and TASK_COMPLEX."""
    config = AgentConfig(name="Queen")
    agent = BaseAgent(config=config)
    
    # Check CHAT
    assert agent._classify_intent("你好") == "CHAT"
    
    # Check TASK_SIMPLE
    assert agent._classify_intent("查天气") == "TASK_SIMPLE"
    assert agent._classify_intent("搜索代码") == "TASK_SIMPLE"
    
    # Check TASK_COMPLEX
    assert agent._classify_intent("分析系统架构") == "TASK_COMPLEX"
    assert agent._classify_intent("重构核心逻辑") == "TASK_COMPLEX"

def test_agent_run_loop_chat():
    """Test the full OODA loop for a simple chat message."""
    config = AgentConfig(name="Queen")
    agent = BaseAgent(config=config)
    transport = MockTransport(inputs=["你好", "exit"])
    
    agent.run(transport)
    
    # Verify sequence
    assert any("已就绪" in msg[1] for msg in transport.sent_messages)
    assert any("意图分类: CHAT" in act[1] for act in transport.reported_actions)

def test_agent_run_loop_task_simple(monkeypatch):
    """Test the fast path for a simple task."""
    monkeypatch.setattr("time.sleep", lambda x: None)
    
    config = AgentConfig(name="Queen")
    agent = BaseAgent(config=config)
    transport = MockTransport(inputs=["查天气", "exit"])
    
    agent.run(transport)
    
    # Verify Queen handled it directly
    assert any("意图分类: TASK_SIMPLE" in act[1] for act in transport.reported_actions)
    assert any("Queen 识别为简单工具请求" in act[1] for act in transport.reported_actions)
    assert any("调用工具: web_search" in act[1] for act in transport.reported_actions)

@pytest.mark.timeout(5)
def test_agent_run_loop_task_complex(monkeypatch):
    """Test the slow path for a complex task."""
    monkeypatch.setattr("time.sleep", lambda x: None)
    
    config = AgentConfig(name="Queen")
    agent = BaseAgent(config=config)
    transport = MockTransport(inputs=["分析架构", "exit"])
    
    agent.run(transport)
    
    # Verify Orchestrator handoff simulation
    assert any("意图分类: TASK_COMPLEX" in act[1] for act in transport.reported_actions)
    assert any("移交给后台 **Orchestrator**" in msg[1] for msg in transport.sent_messages)
    assert any("任务执行计划 (DAG)" in msg[1] for msg in transport.sent_messages)

def test_guardrails_trigger_in_demo(monkeypatch):
    """Test that high-risk keywords trigger the confirmation UI."""
    monkeypatch.setattr("time.sleep", lambda x: None)
    
    config = AgentConfig(name="Queen")
    agent = BaseAgent(config=config)
    transport = MockTransport(inputs=["删除所有文件", "exit"])
    transport.confirmed = False # User says NO
    
    agent.run(transport)
    
    # Verify Guardrails was reported
    assert any("正在进行安全审计" in act[1] for act in transport.reported_actions)
    # Verify refusal was handled
    assert any("用户拒绝执行" in act[1] for act in transport.reported_actions)
    assert any("操作已取消" in msg[1] for msg in transport.sent_messages)
