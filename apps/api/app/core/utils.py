import re


CNPJ_RE = re.compile(r"^\d{14}$")


def normalize_cnpj(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if not CNPJ_RE.match(digits):
        raise ValueError("CNPJ must have 14 digits")
    return digits
