from .server import main, mcp
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Expose important items at package level
__all__ = ["main", "mcp"]

# Allow running directly as a module
if __name__ == "__main__":
    sys.exit(main())
