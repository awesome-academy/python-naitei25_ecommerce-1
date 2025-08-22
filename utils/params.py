from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, List
from django.http import QueryDict


def to_decimal(v: Any) -> Decimal | None:
    """Chuyển v về Decimal; hỗ trợ '1,23' -> Decimal('1.23').
    Trả về None nếu rỗng/không hợp lệ.
    """
    if v in (None, ""):
        return None
    try:
        return Decimal(str(v).replace(",", "."))
    except (InvalidOperation, TypeError, ValueError):
        return None


def getlist(qs_or_qd: QueryDict, name: str) -> List[str]:
    """Lấy list tham số từ QueryDict, hỗ trợ cả `name` và `name[]`."""
    return qs_or_qd.getlist(f"{name}[]") or qs_or_qd.getlist(name)

