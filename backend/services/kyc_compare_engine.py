"""So sánh Live Text vs QR để auto-verify KYC VNeID.

Chỉ so sánh 3 trường: cccd, full_name, date_of_birth.
Chuẩn hóa trước khi so sánh để tránh lỗi encoding / khoảng trắng.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


@dataclass
class CompareResult:
    matched: bool
    mismatches: dict = field(default_factory=dict)
    # mismatches: {field_name: {"live": <original>, "qr": <original>}}


def compare_livetext_qr(live: dict, qr: dict) -> CompareResult:
    """So sánh live_data (từ parse_cccd_live_text) với qr_data (từ decode_qr)."""
    mismatches: dict = {}

    checks = [
        ("cccd",          _norm_cccd, live.get("id_number"),    qr.get("cccd")),
        ("full_name",     _norm_name, live.get("full_name"),     qr.get("full_name")),
        ("date_of_birth", _norm_date, live.get("date_of_birth"), qr.get("date_of_birth")),
    ]

    for fname, norm_fn, live_val, qr_val in checks:
        lv = norm_fn(live_val or "")
        qv = norm_fn(qr_val  or "")
        if lv != qv:
            mismatches[fname] = {"live": live_val, "qr": qr_val}

    return CompareResult(matched=not mismatches, mismatches=mismatches)


# ── Normalizers ────────────────────────────────────────────────────────────────

def _norm_cccd(s: str) -> str:
    return re.sub(r"\D", "", s)


def _norm_name(s: str) -> str:
    s = s.strip().upper()
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\s+", " ", s)
    return _strip_accents(s)


def _strip_accents(s: str) -> str:
    """Bỏ dấu để so sánh khoan nhượng hơn (tránh lỗi encoding VNeID vs Live Text)."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _norm_date(s: str) -> str:
    """Chuẩn hóa về YYYY-MM-DD."""
    s = s.strip()
    m = re.match(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", s)
    if m:
        return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    return s
