from dataclasses import dataclass

@dataclass
class PromptConfig:
    name: str = "indication-landscape"
    description: str = "Analyzes clinical trial patterns, development trends, and competitive dynamics within specific therapeutic areas"
    required_args: list[str] = ("topic",)
    arg_descriptions: dict[str, str] = {
        "topic": "Therapeutic area or indication to analyze (e.g., 'multiple sclerosis', 'breast cancer')"
    }

PROMPT_CONFIG = PromptConfig() 