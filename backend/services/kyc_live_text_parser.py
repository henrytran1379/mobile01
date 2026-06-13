"""Parser CCCD từ iPhone Live Text.

Hàm chính: parse_cccd_live_text(raw_text) -> dict

Không cần OCR, không cần ảnh. User copy text từ iPhone Live Text,
paste vào bot, parser tự nhận diện và chuẩn hóa.

Hỗ trợ:
  - Label + value cùng dòng:  "Giới tính / Sex: Nam"
  - Label + value khác dòng:  "Ngày sinh\n20/01/1979"
  - Song ngữ VI + EN
  - Có dấu hoặc mất dấu (EasyOCR noise)
  - Ký tự thừa / xuống dòng lộn xộn
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional


# ── Constants ─────────────────────────────────────────────────────────────────

REQUIRED_FIELDS = [
    "id_number",
    "full_name",
    "date_of_birth",
    "gender",
    "place_of_residence",
]

OPTIONAL_FIELDS = [
    "nationality",
    "place_of_birth",
    "issue_date",
    "expiry_date",
]

FIELD_LABELS = {
    "id_number": [
        r"s[ốo]\s*[dđ][ịi]nh\s*danh\s*(?:c[áa]\s*nh[aâ]n)?",
        r"personal\s*identification\s*(?:number)?",
        r"s[ốo]\s*cccd",
        r"s[ốo]\s*cmnd",
        r"m[ãa]\s*s[ốo]",
        r"id\s*number",
    ],
    "full_name": [
        r"h[ọo][,\.]?\s*ch[ữu]\s*[dđ][eệ]m\s*v[aà]\s*t[eê]n(?:\s*khai\s*sinh)?",
        r"h[ọo]\s*v[aà]\s*t[eê]n",
        r"h[ọo]\s*t[eê]n",
        r"full\s*name",
    ],
    "date_of_birth": [
        r"ng[aà]y[,\.]?\s*th[aá]ng[,\.]?\s*n[aă]m\s*sinh",
        r"ng[aà]y\s*sinh",
        r"date\s*of\s*birth",
        r"dob",
    ],
    "gender": [
        r"gi[oớ]i\s*t[íi]nh",
        r"sex(?!\w)",
        r"gender",
    ],
    "nationality": [
        r"qu[oố]c\s*t[íị]ch",
        r"nationality",
    ],
    "place_of_residence": [
        r"n[oơ]i\s*c[uư]\s*tr[uú]",
        r"n[oơ]i\s*th[ưu][oờ]ng\s*tr[uú]",
        r"place\s*of\s*residence",
        r"[dđ][iị]a\s*ch[iỉ](?:\s*th[ưu][oờ]ng\s*tr[uú])?",
    ],
    "place_of_birth": [
        r"n[oơ]i\s*[dđ][aă]ng\s*k[yý]\s*khai\s*sinh",
        r"qu[eê]\s*qu[aá]n",
        r"place\s*of\s*(?:birth|origin)",
    ],
    "issue_date": [
        r"ng[aà]y[,\.]?\s*th[aá]ng[,\.]?\s*n[aă]m\s*c[aấ]p",
        r"ng[aà]y\s*c[aấ]p",
        r"date\s*of\s*issue",
        r"c[aấ]p\s*ng[aà]y",
    ],
    "expiry_date": [
        r"ng[aà]y[,\.]?\s*th[aá]ng[,\.]?\s*n[aă]m\s*h[eế]t\s*h[aạ]n",
        r"ng[aà]y\s*h[eế]t\s*h[aạ]n",
        r"c[oó]\s*gi[aá]\s*tr[iị]\s*[dđ][eế]n",
        r"date\s*of\s*expir(?:y|ation)",
        r"expir(?:y|ation)",
        r"h[eế]t\s*h[aạ]n",
    ],
}

# Regex nhận diện ngày dạng DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
_DATE_RE = re.compile(r"\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})\b")

# Regex số ID 9 hoặc 12 chữ số (không phần của ngày tháng)
_ID_RE = re.compile(r"(?<![/\-\.])\b(\d{9}|\d{12})\b(?![/\-\.])")

# Từ khoá trigger: xác định đây là text CCCD
_CCCD_TRIGGERS = re.compile(
    r"c[aă]n\s*c[ưướ][ớo]c|cccd|cmnd"
    r"|s[ốo]\s*[dđ][ịi]nh\s*danh"
    r"|personal\s*identification"
    r"|c[oộ]ng\s*h[oò]a\s*x[aã]",
    re.IGNORECASE,
)


# ── Public API ────────────────────────────────────────────────────────────────

def is_cccd_text(text: str) -> bool:
    """Kiểm tra text có phải Live Text CCCD không (để bot auto-detect)."""
    return bool(_CCCD_TRIGGERS.search(text))


def parse_cccd_live_text(raw_text: str) -> dict:
    """Parse Live Text từ iPhone → dict chuẩn hóa.

    Args:
        raw_text: Chuỗi text thô từ iPhone Live Text, có thể lộn xộn.

    Returns:
        dict với đầy đủ fields, parse_status và missing_fields.
    """
    result: dict[str, object] = {
        "id_number":          None,
        "full_name":          None,
        "date_of_birth":      None,
        "gender":             None,
        "nationality":        None,
        "place_of_residence": None,
        "place_of_birth":     None,
        "issue_date":         None,
        "expiry_date":        None,
        "raw_text":           raw_text,
        "source":             "iphone_live_text",
        "parse_status":       "failed",
        "missing_fields":     [],
    }

    lines = _clean_lines(raw_text)
    if not lines:
        result["missing_fields"] = list(REQUIRED_FIELDS)
        return result

    extracted = _extract_all_fields(lines)

    result["id_number"]          = _norm_id(extracted.get("id_number", ""))
    result["full_name"]          = _norm_name(extracted.get("full_name", ""))
    result["date_of_birth"]      = _norm_date(extracted.get("date_of_birth", ""))
    result["gender"]             = _norm_gender(extracted.get("gender", ""))
    result["nationality"]        = _norm_nationality(extracted.get("nationality", ""))
    result["place_of_residence"] = _norm_addr(extracted.get("place_of_residence", ""))
    result["place_of_birth"]     = _norm_addr(extracted.get("place_of_birth", ""))
    result["issue_date"]         = _norm_date(extracted.get("issue_date", ""))
    result["expiry_date"]        = _norm_date(extracted.get("expiry_date", ""))

    # Fallback: quét toàn text nếu chưa tìm được id_number
    if not result["id_number"]:
        result["id_number"] = _scan_id(raw_text)

    # Fallback dates: gán issue/expiry từ các ngày còn lại trong text
    _fallback_dates(result, raw_text)

    # Validate required fields
    _label_vi = {
        "id_number":          "Số định danh",
        "full_name":          "Họ và tên",
        "date_of_birth":      "Ngày sinh",
        "gender":             "Giới tính",
        "place_of_residence": "Nơi cư trú",
    }
    missing = [_label_vi[f] for f in REQUIRED_FIELDS if not result[f]]
    result["missing_fields"] = missing

    if not missing:
        result["parse_status"] = "success"
    elif len(missing) < len(REQUIRED_FIELDS):
        result["parse_status"] = "partial"
    else:
        result["parse_status"] = "failed"

    return result


# ── Field extractor ───────────────────────────────────────────────────────────

def _extract_all_fields(lines: list[str]) -> dict[str, str]:
    """Tìm value cho từng field theo label.

    Chiến lược:
      1. Cùng dòng — có ":" sau label:  "Quốc tịch / Nationality: Việt Nam"
      2. Cùng dòng — có "." sau EN label: "Giới tính/Sex. Nam,"
      3. Khác dòng — dòng kế tiếp là value: "Ngày sinh\n20/01/1979"
      4. Địa chỉ 2 dòng — nối dòng kế tiếp nếu không phải label mới.
    """
    found: dict[str, str] = {}

    for i, line in enumerate(lines):
        line_lower = line.lower()

        for field, patterns in FIELD_LABELS.items():
            if field in found:
                continue

            for pat in patterns:
                m = re.search(pat, line_lower)
                if not m:
                    continue

                remainder = line[m.end():]

                # Bỏ phần EN label song ngữ rồi lấy value sau ":" hoặc "."
                value = _extract_value_from_remainder(remainder)

                if value and not _is_label(value):
                    # Địa chỉ có thể kéo dài sang dòng kế tiếp
                    if field in ("place_of_residence", "place_of_birth"):
                        value = _merge_address_lines(value, lines, i + 1)
                    found[field] = value
                elif i + 1 < len(lines) and not _is_label(lines[i + 1]):
                    val = lines[i + 1]
                    if field in ("place_of_residence", "place_of_birth"):
                        val = _merge_address_lines(val, lines, i + 2)
                    found[field] = val
                break

    return found


def _extract_value_from_remainder(remainder: str) -> str:
    """Lấy value từ phần sau label, xử lý cả 2 dạng song ngữ.

    Dạng 1: "/ Nationality: Việt Nam"   → "Việt Nam"  (có dấu ":")
    Dạng 2: "/ Sex. Nam,"               → "Nam,"      (có dấu "." sau EN word)
    Dạng 3: ": Việt Nam"                → "Việt Nam"  (trực tiếp)
    Dạng 4: " Nam"                      → "Nam"       (giá trị ngay sau label)
    """
    r = remainder.strip()
    if not r:
        return ""

    # Dạng 1 & 3: có dấu ":" → lấy mọi thứ sau dấu ":" cuối cùng trên dòng
    colon_m = re.search(r'[:：]\s*(.+)$', r)
    if colon_m:
        val = colon_m.group(1).strip()
        # Loại bỏ trailing noise: "Nam," → "Nam"
        return val.rstrip(".,; ")

    # Dạng 2: bắt đầu bằng "/" rồi có "word." → lấy phần sau dấu "."
    # Ví dụ: "/Sex. Nam," hoặc "/ Full name. "
    dot_m = re.search(r'^[/\s]*\w[^.]*\.\s+(.+)$', r)
    if dot_m:
        val = dot_m.group(1).strip().rstrip(".,; ")
        return val

    # Dạng 4: bắt đầu bằng "/" nhưng phần còn lại là chính value
    # (không có EN label): bỏ "/" đầu và lấy
    r_stripped = r.lstrip("/. ").strip()
    return r_stripped.rstrip(".,; ")


def _merge_address_lines(first_line: str, lines: list[str], next_idx: int) -> str:
    """Nối dòng kế tiếp vào địa chỉ nếu nó là phần tiếp theo (không phải label mới)."""
    result = first_line.strip()
    if next_idx < len(lines):
        next_ln = lines[next_idx].strip()
        if next_ln and not _is_label(next_ln) and not _looks_like_section(next_ln):
            result = result + ", " + next_ln if result else next_ln
    return result


def _looks_like_section(text: str) -> bool:
    """Các dòng tiêu đề như 'Mặt sau', 'BỘ CÔNG AN', 'Căn cước điện tử'."""
    t = text.strip()
    return bool(re.match(
        r"^(m[aặ]t\s*(tr[ưướ][ớo]c|sau)|b[oộ]\s*c[oô]ng\s*an|"
        r"c[aă]n\s*c[ưướ][ớo]c\s*[dđ][iị]ện|"
        r"l[iị]ch\s*s[ửu]|socialist|independence|c[oộ]ng\s*h[oò]a)",
        t, re.IGNORECASE,
    ))


def _is_label(text: str) -> bool:
    """Kiểm tra text có phải label của field nào không."""
    t = text.lower().strip()
    for patterns in FIELD_LABELS.values():
        for pat in patterns:
            if re.search(pat, t):
                return True
    return False


# ── Normalizers ───────────────────────────────────────────────────────────────

def _norm_id(raw: str) -> Optional[str]:
    """Chỉ giữ số; chỉ trả về nếu đúng 12 chữ số (CCCD)."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 12:
        return digits
    return None


def _scan_id(text: str) -> Optional[str]:
    """Fallback: quét toàn text tìm chuỗi 12 chữ số liên tiếp."""
    for m in _ID_RE.finditer(text):
        cand = m.group(1)
        if len(cand) == 12:
            return cand
    return None


def _norm_name(raw: str) -> Optional[str]:
    """Giữ Unicode tiếng Việt, viết hoa toàn bộ, bỏ ký tự đặc biệt."""
    if not raw:
        return None
    # Bỏ dòng con chứa label tiếng Anh ở cuối
    raw = re.sub(r"\s*/\s*Full\s*name.*$", "", raw, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"[^\w\s]", " ", raw, flags=re.UNICODE)
    cleaned = " ".join(cleaned.split())  # chuẩn hóa khoảng trắng
    return cleaned.upper() if len(cleaned) >= 2 else None


def _norm_date(raw: str) -> Optional[str]:
    """Chuẩn hóa DD/MM/YYYY → YYYY-MM-DD."""
    if not raw:
        return None
    m = _DATE_RE.search(raw)
    if not m:
        return None
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100):
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def _norm_gender(raw: str) -> Optional[str]:
    """Nam/Male → 'male', Nữ/Female → 'female'."""
    if not raw:
        return None
    t = raw.strip().lower()
    # Tách phần tiếng Anh song ngữ "Nam / Male"
    t = re.split(r"[/|]", t)[0].strip()
    if t in ("nam", "male", "m"):
        return "male"
    if t in ("nữ", "nu", "nư", "female", "f"):
        return "female"
    return None


def _norm_nationality(raw: str) -> Optional[str]:
    """Việt Nam → 'Vietnam'."""
    if not raw:
        return None
    if re.search(r"vi[eệ]t\s*nam|vietnam", raw, re.IGNORECASE):
        return "Vietnam"
    return raw.strip() or None


def _norm_addr(raw: str) -> Optional[str]:
    """Chuẩn hóa địa chỉ: giữ Unicode, bỏ trailing label."""
    if not raw:
        return None
    cleaned = raw.strip()
    # Cắt nếu gặp label mới ở đầu từ (không cắt giữa chữ như "Hoàng", "Thọ")
    # Chỉ cắt khi keyword xuất hiện ở đầu từ và theo sau bằng space/newline
    cleaned = re.sub(
        r"\s+(?:ng[aà]y\s|n[oơ]i\s|qu[oố]c\s|gi[oớ]i\s|place\s|date\s|sex\s|gender\s).*$",
        "", cleaned, flags=re.IGNORECASE,
    ).strip()
    return cleaned if len(cleaned) >= 3 else None


def _fallback_dates(result: dict, raw_text: str) -> None:
    """Nếu chưa có issue/expiry, tìm ngày còn lại trong text rồi gán."""
    all_dates: list[str] = []
    for m in _DATE_RE.finditer(raw_text):
        d = _norm_date(m.group(0))
        if d:
            all_dates.append(d)

    # Loại trừ ngày đã biết
    known = {result.get("date_of_birth")}
    remaining = [d for d in all_dates if d not in known]

    if not result["issue_date"] and remaining:
        # Ngày cấp: ngày gần nhất >= 2020
        recent = sorted([d for d in remaining if d >= "2020-01-01"])
        if recent:
            result["issue_date"] = recent[0]
            remaining = [d for d in remaining if d != recent[0]]

    if not result["expiry_date"] and remaining:
        # Ngày hết hạn: ngày xa nhất trong tương lai
        future = sorted([d for d in remaining if d > (result.get("issue_date") or "2020-01-01")])
        if future:
            result["expiry_date"] = future[-1]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_lines(text: str) -> list[str]:
    """Tách dòng, bỏ dòng trống và nhiễu ngắn."""
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        # Bỏ dòng chỉ có dấu chấm, gạch, số trang, hoặc quá ngắn (1-2 ký tự)
        if not ln or re.match(r"^[\.\-\*\s\d]{0,3}$", ln):
            continue
        lines.append(ln)
    return lines
