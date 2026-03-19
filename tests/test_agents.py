import os
import pytest
from agents import Agent, MainAgent

def test_agent_initialization():
    agent = Agent("Test Agent")
    assert agent.name == "Test Agent"
    assert agent.skills == []
    assert agent.skill_instructions == ""

def test_agent_add_skill():
    agent = Agent("Test Agent")
    agent.add_skill("Coding")
    assert "Coding" in agent.skills
    assert "- Coding" in agent.skill_instructions

def test_agent_mock_execution():
    # Ensure it falls back to mock when no keys/ollama are present
    agent = Agent("Test Agent")
    result = agent.execute_task("Hello")
    assert "[MOCK]" in result
    assert "Hello" in result

def test_main_agent_orchestration():
    main = MainAgent()
    assert main.name == "Main Agent"
    assert main.security_agent is not None
    
    # Test delegation (mock mode)
    result = main.delegate("Test task", main.python_coder)
    assert "delegated to" in result
    assert "[MOCK]" in result
