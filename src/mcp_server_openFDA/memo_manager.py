import logging

logger = logging.getLogger('mcp_openfda_server.memo_manager')

class MemoManager:
    def __init__(self):
        self.drug_insights: list[str] = []
        logger.info("MemoManager initialized")

    def add_drug_insight(self, insight: str) -> None:
        """Add a new drug-related insight from OpenFDA data"""
        if not insight:
            logger.error("Attempted to add empty insight")
            raise ValueError("Empty insight")
        
        self.drug_insights.append(insight)
        logger.debug(f"Added new drug insight. Total insights: {len(self.drug_insights)}")

    def get_landscape_memo(self) -> str:
        """Generate a formatted memo from collected drug insights"""
        logger.debug(f"Generating landscape memo with {len(self.drug_insights)} insights")
        if not self.drug_insights:
            logger.info("No drug insights available")
            return "No drug analysis available yet."

        insights = "\n".join(f"- {insight}" for insight in self.drug_insights)
        logger.debug("Generated landscape memo")
        
        memo = "🔍 Drug Data Analysis\n\n"
        memo += "Key Insights from OpenFDA:\n\n"
        memo += insights

        if len(self.drug_insights) > 1:
            memo += "\n\nSummary:\n"
            memo += f"Analysis has identified {len(self.drug_insights)} key insights from OpenFDA data."

        return memo