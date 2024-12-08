import logging

logger = logging.getLogger('mcp_aact_server.memo_manager')

class MemoManager:
    def __init__(self):
        self.insights: list[str] = []
        self.landscape_findings: list[str] = []
        self.metrics_findings: list[str] = []
        logger.info("MemoManager initialized")

    def add_landscape_finding(self, finding: str) -> None:
        """Add a new trial landscape finding to the in-memory collection"""
        if not finding:
            logger.error("Attempted to add empty landscape finding")
            raise ValueError("Empty landscape finding")
        
        self.landscape_findings.append(finding)
        logger.debug(f"Added new landscape finding. Total findings: {len(self.landscape_findings)}")

    def get_landscape_memo(self) -> str:
        """Generate a formatted memo from collected trial landscape findings"""
        logger.debug(f"Generating landscape memo with {len(self.landscape_findings)} findings")
        if not self.landscape_findings:
            logger.info("No landscape findings available")
            return "No landscape analysis available yet."

        findings = "\n".join(f"- {finding}" for finding in self.landscape_findings)
        logger.debug("Generated landscape memo")
        
        memo = "🔍 Clinical Trial Landscape Analysis\n\n"
        memo += "Key Development Patterns & Trends:\n\n"
        memo += findings

        if len(self.landscape_findings) > 1:
            memo += "\n\nSummary:\n"
            memo += f"Analysis has identified {len(self.landscape_findings)} key patterns in trial development."

        return memo

