import pytest
from agents import Agent

def test_system_handling_issue_5():
    """
    Verification for Issue #5 (Test Issue).
    Ensures the agent system correctly initializes 
    and returns a valid response to test queries.
    """
    agent = Agent("Issue 5 Verifier")
    response = agent.execute_task("Self-test for GitHub Issue #5 resolution.")
    
    # Assert successful mock/real execution
    assert response is not None
    assert len(response) > 0
    assert "GitHub Issue #5" in response or "[MOCK]" in response
