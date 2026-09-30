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
TOOL_AUTHORIZATION_CONTRACT = "explicit-request-v2"
TOOL_AUTHORIZATION_CONTRACTS = {"explicit-request-v1", TOOL_AUTHORIZATION_CONTRACT}
PRICE_LOOKUP = (
    r"(?:look\s+up|check|fetch|retrieve|find|show(?:\s+me)?|tell\s+me|what\s+is)"
    r"\s+(?:the\s+)?(?:(?:actual|current|live|unit)\s+)?(?:price|cost)\b(?!\s+(?:cap|ceiling|limit)\b)"
)


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


def tool_permissions(query: str, *, contract: str = TOOL_AUTHORIZATION_CONTRACT) -> dict:
    """Authorize business tools from the request, not merely the presence of a SKU."""
    if contract not in TOOL_AUTHORIZATION_CONTRACTS:
        raise ValueError("Unknown business-tool authorization contract.")
    skus = sorted({match.upper() for match in re.findall(SKU_PATTERN, query)})
    if len(skus) > 3:
        raise ToolInputError("At most three explicit inventory SKUs may be checked per turn.")
    no_actions = bool(re.search(
        r"\bpolicy[- ]only\b|\busing policy only\b|\bbefore any (?:lookup|draft)\b|"
        r"\bdo not (?:execute|run|call)(?: any)? (?:tools?|anything)\b|"
        r"(?:정책|규정)만|도구[^.!?\n]{0,30}(?:실행|호출)하지",
        query, re.I,
    ))
    draft_requested = bool(re.search(
        r"\b(?:prepare|create|make|generate)\b[^.!?\n]{0,160}\b(?:drafts?|purchase[- ]request)\b|"
        r"\bdraft (?:a|an|the|for)\b|초안[^.!?\n]{0,30}(?:만들|작성|준비)|초안\s*$",
        query, re.I,
    ))
    no_draft = bool(re.search(
        r"\b(?:do not|don't|without|not requesting)\b[^.!?\n]{0,100}\b(?:drafts?|requests?)\b|"
        r"초안[^.!?\n]{0,30}(?:만들지|작성하지)|초안 없이",
        query, re.I,
    ))
    no_stock = bool(re.search(
        r"\b(?:do not|don't|without)\s+(?:(?:look(?:ing)? up|check(?:ing)?|query(?:ing)?|"
        r"fetch(?:ing)?|use|using)\s+(?:the |any )?(?:stock|inventory|get_stock)|"
        r"(?:a |any )?(?:stock|inventory)\s+(?:lookup|check|query)|lookups?)\b|"
        r"재고[^.!?\n]{0,30}조회하지|조회 없이",
        query, re.I,
    ))
    stock_requested = bool(re.search(
        r"\b(?:stock|inventory|availability|available|lead[- ]times?)\b|"
        r"\b(?:actual|current|live|unit)\s+prices?\b|"
        r"재고|납기|실제\s*(?:단가|가격)",
        query, re.I,
    ))
    if contract == TOOL_AUTHORIZATION_CONTRACT:
        stock_requested = stock_requested or bool(re.search(r"\b" + PRICE_LOOKUP, query, re.I))
        no_stock = no_stock or bool(re.search(r"\b(?:do not|don't|never)\s+" + PRICE_LOOKUP, query, re.I))
    drafts = []
    if draft_requested and not no_actions and not no_draft:
        for sku in skus:
            for value in sorted(quantities(query)):
                if not re.fullmatch(r"\+?\d+", value) or not 1 <= int(value) <= 10:
                    continue
                arguments = {"sku": sku, "quantity": int(value)}
                try:
                    validate_draft_request(query, arguments)
                except ToolInputError:
                    continue
                if arguments not in drafts:
                    drafts.append(arguments)
        if len(drafts) != len(skus):
            drafts = []
    stock_skus = (
        skus if not no_actions and not no_stock and (stock_requested or drafts) else []
    )
    return {
        "stock_skus": stock_skus, "draft_arguments": drafts,
        "draft_requested": draft_requested,
        "draft_needs_clarification": draft_requested and not drafts and not no_actions and not no_draft,
        "business_actions_forbidden": no_actions,
    }


def validate_business_tool_request(
    query: str, name: str, arguments: dict, *, contract: str = TOOL_AUTHORIZATION_CONTRACT,
) -> None:
    permissions = tool_permissions(query, contract=contract)
    if not isinstance(arguments, dict):
        raise ToolInputError("Business tool arguments must be an object.")
    if name == "get_stock":
        if set(arguments) != {"sku"} or arguments["sku"] not in permissions["stock_skus"]:
            raise ToolInputError("Stock lookup was not authorized by this request; no lookup was executed.")
    elif name == "prepare_purchase_request":
        validate_draft_request(query, arguments)
        if arguments not in permissions["draft_arguments"]:
            raise ToolInputError("No explicit, valid draft request was authorized; no draft was created.")
    else:
        raise ToolInputError("Only the declared stock and draft tools are allowed.")


def required_policy_citations(query: str, *, contract: str = TOOL_AUTHORIZATION_CONTRACT) -> list[str]:
    """Policy obligations for draft boundaries and approval claims, independent of eval cases."""
    if contract not in TOOL_AUTHORIZATION_CONTRACTS:
        raise ValueError("Unknown citation-obligation contract.")
    if contract == TOOL_AUTHORIZATION_CONTRACT:
        query = re.sub(
            r"\bapproved\s+(?:(?:daily|current|official)\s+)?"
            r"(?:(?:foreign[- ]exchange|exchange|conversion|currency|FX)\s+rates?)\b",
            "exchange rate", query, flags=re.I,
        )

        def tool_prohibition(match):
            clause = match[0]
            # Keep judgments and counter-instructions; omit only a pure no-draft tool directive.
            if re.search(r"\b(?:approvals?|approved|approvers?|orders?|payments?|paid|pay|but|instead|unless|except|however)\b", clause, re.I):
                return clause
            if re.search(r"\b(?:create|prepare|make|generate)\b[^.!?;\n]*\bdrafts?\b", clause, re.I):
                return ""
            return clause

        query = re.sub(r"\b(?:do not|don't|never)\b[^.!?;\n]*", tool_prohibition, query, flags=re.I)
    ids = set()
    approval = bool(re.search(r"\b(?:approvals?|approved|approvers?)\b|승인", query, re.I))
    if approval:
        ids.add("CONTOSO-PROC-2026-09-s3")
    if re.search(r"\b(?:drafts?|purchase[- ]requests?|orders?|payments?|paid)\b|초안|주문|결제", query, re.I):
        ids.add("CONTOSO-PROC-2026-09-s4")
    if approval and re.search(
        r"\b(?:documents?|exports?|notes?|memos?|system|backend|claims?|verbal|says?|said|"
        r"instructions?|tool results?)\b|문서|메모|주장|도구\s*결과",
        query, re.I,
    ):
        ids.add("CONTOSO-SEC-2026-09-s4")
    return sorted(ids)
