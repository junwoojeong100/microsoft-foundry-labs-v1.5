"""Ground draft arguments in explicit user input; never accept invented quantities."""

import re

from workshop import LANGUAGE, ToolInputError

SKU_PATTERN = r"(?<![A-Za-z0-9_-])[A-Za-z]{2,4}-\d{2,3}(?![A-Za-z0-9_-])"
KOREAN_QUANTITIES = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10}
ENGLISH_QUANTITIES = {
    word: number for number, word in enumerate((
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen", "twenty",
    ))
}
ENGLISH_QUANTITIES.update({"thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
                          "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000})
ENGLISH_VALUE = r"(?:[+-]?\d+(?:\.\d+)?|(?:(?:minus|negative)\s+)?(?:" + "|".join(ENGLISH_QUANTITIES) + r"))"
ENGLISH_EXPRESSION = ENGLISH_VALUE + r"(?:(?:\s+(?:(?:and|or|to)\s+)?|[-–]\s*)" + ENGLISH_VALUE + r")*"
ENGLISH_UNITS = r"(?:units?|items?|pcs?|laptops?|notebooks?|monitors?|keyboards?)"


def english_quantities(text: str) -> set[str]:
    values = set()
    patterns = (
        rf"(?<![A-Za-z0-9_.+-])(?P<value>{ENGLISH_EXPRESSION})\s+(?:{SKU_PATTERN}(?:\s+{ENGLISH_UNITS})?|{ENGLISH_UNITS})\b",
        rf"\b(?:quantity|qty)\s*(?:(?:is|of)\s+|[:=]\s*)?(?P<value>{ENGLISH_EXPRESSION})(?![A-Za-z0-9_-]|\.\d)",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.I):
            value = match["value"].lower()
            if not re.fullmatch(ENGLISH_VALUE, value):
                values.add("ambiguous")
            elif re.fullmatch(r"[+-]?\d+(?:\.\d+)?", value):
                values.add(value)
            else:
                words = value.split()
                sign = -1 if words[0] in {"minus", "negative"} else 1
                values.add(str(sign * ENGLISH_QUANTITIES[words[-1]]))
    return values


def quantities(text: str) -> set[str]:
    values = set(re.findall(r"(?<![A-Za-z0-9_.+-])([+-]?\d+(?:\.\d+)?)\s*(?:대|개|units?|items?|pcs?)(?![A-Za-z])", text, re.I))
    values.update(re.findall(r"(?:수량|quantity|qty)\s*(?:은|는|:|=)?\s*([+-]?\d+(?:\.\d+)?)", text, re.I))
    for word, number in KOREAN_QUANTITIES.items():
        if re.search(r"(?<![가-힣])" + word + r"\s*(?:대|개)", text):
            values.add(str(number))
    if LANGUAGE == "en":
        values.update(english_quantities(text))
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
        if LANGUAGE == "en":
            previous = max((match.end() for match in matches if match.end() < matching[0].start()), default=0)
            prefix = query[previous:matching[0].start()]
            if "ambiguous" in english_quantities(prefix + sku + text):
                raise ToolInputError("Ambiguous quantity; provide one quantity for each requested SKU.")
            separators = r"\b(?:and|plus)\b|[;\n]"
            prefix = re.split(separators, prefix, flags=re.I)[-1]
            suffix = re.split(separators, text, flags=re.I)[0]
            stated = quantities(prefix + sku) | quantities(suffix)
        else:
            stated = quantities(text)
    else:
        stated = quantities(text)
    if len(stated) != 1 or not re.fullmatch(r"\+?\d+", next(iter(stated), "")) or int(next(iter(stated))) != quantity:
        raise ToolInputError("A single explicit, matching integer quantity is required; ask for clarification instead of guessing or reducing it.")
