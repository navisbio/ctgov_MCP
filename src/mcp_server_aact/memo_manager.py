import logging

logger = logging.getLogger('mcp_aact_server.memo_manager')

class MemoManager:
    def __init__(self):
        self.insights: list[str] = []
        logger.info("MemoManager initialized")

    def add_insights(self, finding: str) -> None:
        """Add a new trial landscape finding to the in-memory collection"""
        if not finding:
            logger.error("Attempted to add empty landscape finding")
            raise ValueError("Empty landscape finding")
        
        self.insights.append(finding)
        logger.debug(f"Added new landscape finding. Total findings: {len(self.insights)}")

    def get_insights_memo(self) -> str:
        """Generate a formatted memo from collected trial landscape findings"""
        logger.debug(f"Generating landscape memo with {len(self.insights)} findings")
        if not self.insights:
            logger.info("No landscape findings available")
            return "No landscape analysis available yet."

        findings = "\n".join(f"- {finding}" for finding in self.insights)
        logger.debug("Generated landscape memo")
        
        memo = "🔍 Clinical Trial Landscape Analysis\n\n"
        memo += "Key Development Patterns & Trends:\n\n"
        memo += findings

        if len(self.insights) > 1:
            memo += "\n\nSummary:\n"
            memo += f"Analysis has identified {len(self.insights)} key patterns in trial development."

        return memo

