import pytest
from mcp_server_aact.memo_manager import MemoManager

@pytest.fixture
def memo_manager():
    return MemoManager()

def test_add_insights(memo_manager):
    finding = "Test finding"
    memo_manager.add_insights(finding)
    assert len(memo_manager.insights) == 1
    assert memo_manager.insights[0] == finding

def test_add_empty_landscape_finding(memo_manager):
    with pytest.raises(ValueError, match="Empty landscape finding"):
        memo_manager.add_insights("")

def test_get_insights_memo_empty(memo_manager):
    result = memo_manager.get_insights_memo()
    assert "No landscape analysis available yet" in result

def test_get_insights_memo_with_findings(memo_manager):
    memo_manager.add_insights("Finding 1")
    memo_manager.add_insights("Finding 2")
    result = memo_manager.get_insights_memo()
    assert "Finding 1" in result
    assert "Finding 2" in result
    assert "Analysis has identified 2 key patterns" in result 