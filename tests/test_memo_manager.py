import pytest
from mcp_server_aact.memo_manager import MemoManager

@pytest.fixture
def memo_manager():
    return MemoManager()

def test_add_landscape_finding(memo_manager):
    finding = "Test finding"
    memo_manager.add_landscape_finding(finding)
    assert len(memo_manager.landscape_findings) == 1
    assert memo_manager.landscape_findings[0] == finding

def test_add_empty_landscape_finding(memo_manager):
    with pytest.raises(ValueError, match="Empty landscape finding"):
        memo_manager.add_landscape_finding("")

def test_get_landscape_memo_empty(memo_manager):
    result = memo_manager.get_landscape_memo()
    assert "No landscape analysis available yet" in result

def test_get_landscape_memo_with_findings(memo_manager):
    memo_manager.add_landscape_finding("Finding 1")
    memo_manager.add_landscape_finding("Finding 2")
    result = memo_manager.get_landscape_memo()
    assert "Finding 1" in result
    assert "Finding 2" in result
    assert "Analysis has identified 2 key patterns" in result

def test_add_metrics_finding(memo_manager):
    metric = "Test metric"
    memo_manager.add_metrics_finding(metric)
    assert len(memo_manager.metrics_findings) == 1
    assert memo_manager.metrics_findings[0] == metric

def test_add_empty_metrics_finding(memo_manager):
    with pytest.raises(ValueError, match="Empty metric"):
        memo_manager.add_metrics_finding("")

def test_get_metrics_memo_empty(memo_manager):
    result = memo_manager.get_metrics_memo()
    assert "No metrics available yet" in result

def test_get_metrics_memo_with_findings(memo_manager):
    memo_manager.add_metrics_finding("Metric 1")
    memo_manager.add_metrics_finding("Metric 2")
    result = memo_manager.get_metrics_memo()
    assert "Metric 1" in result
    assert "Metric 2" in result
    assert "Analysis has captured 2 key metrics" in result 