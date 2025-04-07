import re
from typing import Dict, Any, Optional, Tuple
from src.rapidapi_toolllm.models.tool import Tool

class SemanticParser:
    def __init__(self):
        self.patterns = {
            "weather": [
                r"(?:what'?s|get|show|tell me) (?:the )?weather (?:in|for|at) (.+?)(?:\s+in\s+(en|vi|ja|ko|zh|ru|fr|es|de|it))?$",
                r"weather (?:in|for|at) (.+?)(?:\s+in\s+(en|vi|ja|ko|zh|ru|fr|es|de|it))?$",
                r"how'?s the weather (?:in|for|at) (.+?)(?:\s+in\s+(en|vi|ja|ko|zh|ru|fr|es|de|it))?$"
            ],
            "news": [
                r"(?:get|show|find|search for) (?:latest|recent) news (?:about|on) (.+?)(?:\s+in\s+(en|vi|fr|es|de|it|ja|ko|zh|ru))?$",
                r"news (?:about|on) (.+?)(?:\s+in\s+(en|vi|fr|es|de|it|ja|ko|zh|ru))?$",
                r"what'?s new (?:about|on) (.+?)(?:\s+in\s+(en|vi|fr|es|de|it|ja|ko|zh|ru))?$"
            ],
            "currency": [
                r"(?:convert|change|exchange) (\d+(?:\.\d+)?) ([A-Z]{3}) (?:to|in) ([A-Z]{3})",
                r"what (?:is|are) (\d+(?:\.\d+)?) ([A-Z]{3}) (?:in|to) ([A-Z]{3})",
                r"how much (?:is|are) (\d+(?:\.\d+)?) ([A-Z]{3}) (?:in|to) ([A-Z]{3})"
            ],
            "movie": [
                r"(?:find|search|get|show) (?:information about|details for) (.+)",
                r"(?:find|search|get|show) movie (.+)",
                r"movie information for (.+)"
            ],
            "recipe": [
                r"(?:find|search|get|show) (?:a )?recipe (?:for|to make) (.+)",
                r"(?:find|search|get|show) (?:how to make|how to cook) (.+)",
                r"recipe (?:for|to make) (.+)"
            ]
        }

    def parse(self, query: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Parse a natural language query to identify the tool and parameters
        Returns: (tool_name, parameters) or (None, None) if no match
        """
        query = query.lower().strip()

        # Check weather patterns
        for pattern in self.patterns["weather"]:
            match = re.search(pattern, query)
            if match:
                city = match.group(1).strip().lower()
                lang = "EN"  # Default to English
                
                # Check if language is specified
                if len(match.groups()) > 1 and match.group(2):
                    lang_map = {
                        "en": "EN", "vi": "VI", "ja": "JA", "ko": "KO",
                        "zh": "ZH", "ru": "RU", "fr": "FR", "es": "ES",
                        "de": "DE", "it": "IT"
                    }
                    lang = lang_map.get(match.group(2).lower(), "EN")
                
                return "weather", {
                    "city": city,
                    "lang": lang
                }

        # Check news patterns
        for pattern in self.patterns["news"]:
            match = re.search(pattern, query)
            if match:
                query_text = match.group(1).strip()
                language = "en"  # Default to English
                
                # Check if language is specified
                if len(match.groups()) > 1 and match.group(2):
                    language = match.group(2).lower()
                
                return "news", {
                    "query": query_text,
                    "language": language
                }
                
        # Check currency patterns
        for pattern in self.patterns["currency"]:
            match = re.search(pattern, query)
            if match:
                amount = float(match.group(1))
                from_currency = match.group(2).upper()
                to_currency = match.group(3).upper()
                return "currency", {
                    "from": from_currency,
                    "to": to_currency,
                    "amount": amount
                }
                
        # Check movie patterns
        for pattern in self.patterns["movie"]:
            match = re.search(pattern, query)
            if match:
                title = match.group(1).strip()
                return "movie", {
                    "title": title
                }
                
        # Check recipe patterns
        for pattern in self.patterns["recipe"]:
            match = re.search(pattern, query)
            if match:
                return "recipe", {"query": match.group(1).strip()}

        return None, None 