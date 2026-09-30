"""Ground draft arguments in explicit user input; never accept invented quantities."""

import re

from workshop import ToolInputError

SKU_PATTERN = r"(?<![A-Za-z0-9_-])[A-Za-z]{2,4}-\d{2,3}(?![A-Za-z0-9_-])"
KOREAN_QUANTITIES = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10}


def quantities(text: str) -> set[str]:
    values = set(re.findall(r"(?<![A-Za-z0-9_.+-])([+-]?\d+(?:\.\d+)?)\s*(?:대|개|units?|items?|pcs?)(?![A-Za-z])", text, re.I))
    values.update(re.findall(r"(?:수량|quantity|qty)\s*(?:은|는|:|=)?\s*([+-]?\d+(?:\.\d+)?)", text, re.I))
    for word, number in KOREAN_QUANTITIES.items():
        if re.search(r"(?<![가-힣])" + word + r"\s*(?:대|개)", text):
            values.add(str(number))
    return values


def validate_draft_request(query: str, arguments: dict) -> None:
    if not isinstance(arguments, dict):
        raise ToolInputError("Draft arguments must be an object.")
    sku, quantity = arguments.get("sku"), arguments.get("quantity")
    if not isinstance(sku, str) or type(quantity) is not int or not 1 <= quantity <= 10:
        raise ToolInputError("Draft quantity must be an integer from 1 through 10; no draft was created.")
    matches = list(re.finditer(SKU_PATTERN, query))
    matching = [match for match in matches if match[0].upper() == sku]
    if not matching:
        raise ToolInputError("The user must explicitly supply the SKU before a draft is created.")
    text = query
    if len({match[0].upper() for match in matches}) > 1:
        start = matching[0].end()
        end = next((match.start() for match in matches if match.start() > start), len(query))
        text = query[start:end]
    stated = quantities(text)
    if len(stated) != 1 or not re.fullmatch(r"\+?\d+", next(iter(stated), "")) or int(next(iter(stated))) != quantity:
        raise ToolInputError("A single explicit, matching integer quantity is required; ask for clarification instead of guessing or reducing it.")
