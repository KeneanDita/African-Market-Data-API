"""Small helpers for cleaning values coming from upstream data sources."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

# Numeric(20, 6) upper bound; anything beyond is almost certainly a sentinel or unit error.
_MAX_ABS = Decimal("1e14")


def parse_number(raw) -> Decimal | None:
    """Coerce upstream values (str/int/float/None/'..'/'n/a') into a Decimal or None."""
    if raw is None:
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        if raw != raw:  # NaN
            return None
        value = Decimal(str(raw))
    else:
        text = str(raw).strip().replace(",", "")
        if text in ("", "..", "-", "n/a", "N/A", "null", "NaN", "no data"):
            return None
        try:
            value = Decimal(text)
        except InvalidOperation:
            return None
    if value.is_nan() or value.is_infinite() or abs(value) > _MAX_ABS:
        return None
    return value.quantize(Decimal("0.000001"))


def parse_year(raw) -> int | None:
    """Accepts 2023, '2023', '2023M01', '2023Q1' and returns the 4-digit year."""
    if raw is None:
        return None
    text = str(raw).strip()[:4]
    if len(text) == 4 and text.isdigit():
        year = int(text)
        if 1900 <= year <= 2100:
            return year
    return None


def clean_iso2_list(raw: str, upper: bool = True) -> list[str]:
    """Split 'et, ng,,KE' into ['ET','NG','KE'] preserving order, dropping dupes/blanks."""
    seen: set[str] = set()
    out: list[str] = []
    for part in raw.split(","):
        code = part.strip()
        if upper:
            code = code.upper()
        if code and code not in seen:
            seen.add(code)
            out.append(code)
    return out
