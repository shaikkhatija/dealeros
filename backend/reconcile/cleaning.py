import re
from decimal import Decimal, InvalidOperation


def normalize_ref(raw):
    match = re.search(r"\d+", raw or "")
    return f"REC-{match.group()}" if match else None


def parse_amount(raw):
    text = (raw or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None
