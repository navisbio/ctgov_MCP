import logging

logger = logging.getLogger('mcp_aact_server.memo_manager')

class MemoManager:
    def __init__(self):
        self.insights: list[str] = []
        self.landscape_findings: list[str] = []
        self.metrics_findings: list[str] = []
        logger.info("MemoManager initialized")

    def add_landscape_finding(self, finding: str) -> None:
        """Add a new landscape finding to the in-memory collection"""
        if not finding:
            logger.error("Attempted to add empty landscape finding")
            raise ValueError("Empty landscape finding")
        
        self.landscape_findings.append(finding)
        logger.debug(f"Added new landscape finding. Total findings: {len(self.landscape_findings)}")

    def get_landscape_memo(self) -> str:
        """Generate a formatted memo from collected landscape findings"""
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

    def add_metrics_finding(self, metric: str) -> None:
        """Add a new metric to the in-memory collection"""
        if not metric:
            logger.error("Attempted to add empty metric")
            raise ValueError("Empty metric")
            
        self.metrics_findings.append(metric)
        logger.debug(f"Added new metric. Total metrics: {len(self.metrics_findings)}")

    def get_metrics_memo(self) -> str:
        """Generate a formatted memo from collected metrics"""
        logger.debug(f"Generating metrics memo with {len(self.metrics_findings)} metrics")
        if not self.metrics_findings:
            logger.info("No metrics available")
            return "No metrics available yet."

        metrics = "\n".join(f"- {metric}" for metric in self.metrics_findings)
        logger.debug("Generated metrics memo")
        
        memo = "📊 Clinical Trial Metrics Summary\n\n"
        memo += "Key Quantitative Findings:\n\n"
        memo += metrics

        if len(self.metrics_findings) > 1:
            memo += "\n\nOverview:\n"
            memo += f"Analysis has captured {len(self.metrics_findings)} key metrics about trial activity."

        return memo 