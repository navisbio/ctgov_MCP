import logging

logger = logging.getLogger('mcp_aact_server.memo_manager')

class MemoManager:
    def __init__(self):
        """Initialize the memo manager for storing clinical trial insights"""
        self.insights: list[str] = []
        logger.info("MemoManager initialized")

    def add_insights(self, finding: str) -> None:
        """Add a new trial insight to the in-memory collection"""
        if not finding:
            logger.error("Attempted to add empty insight")
            raise ValueError("Empty insight")
        
        self.insights.append(finding)
        logger.debug(f"Added new insight. Total insights: {len(self.insights)}")

    def get_insights_memo(self) -> str:
        """Generate a formatted memo from collected trial insights"""
        logger.debug(f"Generating insights memo with {len(self.insights)} findings")
        if not self.insights:
            logger.info("No insights available")
            return "No clinical trial analysis available yet."

        findings = "\n".join(f"- {finding}" for finding in self.insights)
        
        memo = "🔍 Clinical Trial Landscape Analysis\n\n"
        memo += "Key Development Patterns & Trends:\n\n"
        memo += findings

        if len(self.insights) > 1:
            memo += "\n\nSummary:\n"
            memo += f"Analysis has identified {len(self.insights)} key patterns in trial development."

        return memo

