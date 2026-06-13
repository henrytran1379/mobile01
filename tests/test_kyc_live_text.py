"""Unit tests cho live_text_parser — 10 test cases theo spec.

Run: python -m pytest tests/test_kyc_live_text.py -v
"""
import pytest
from backend.kyc.parsers.live_text_parser import parse_live_text, ParseResult


# ── Test 1: Full VNeID text (tất cả fields) ──────────────────────────────────

SAMPLE_FULL = """
Căn cước công dân
Số định danh cá nhân: 042079016888
Họ, chữ đệm và tên khai sinh: NGUYỄN VĂN AN
Ngày, tháng, năm sinh: 15/03/1990
Giới tính: Nam
Quốc tịch: Việt Nam
Nơi cư trú: Số 12 Lê Lợi, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh
Nơi đăng ký khai sinh: Quận Bình Thạnh, TP. Hồ Chí Minh
Ngày cấp: 20/08/2023
Có giá trị đến: 15/03/2035
"""

def test_full_parse():
    r = parse_live_text(SAMPLE_FULL)
    assert r.id_number == "042079016888"
    assert r.full_name == "NGUYỄN VĂN AN"
    assert r.date_of_birth == "1990-03-15"
    assert r.gender == "male"
    assert r.nationality == "Vietnam"
    assert "Hồ Chí Minh" in r.place_of_residence
    assert r.parse_status == "ok"
    assert r.missing_fields == []


# ── Test 2: Label và value khác dòng ─────────────────────────────────────────

SAMPLE_MULTILINE = """
Số định danh cá nhân
042079016888
Họ và tên
TRẦN THỊ BÌNH
Ngày sinh
20/05/1985
Giới tính
Nữ
Quốc tịch
Việt Nam
Nơi cư trú
123 Nguyễn Huệ, Phường 1, Quận 1, TP.HCM
"""

def test_multiline_labels():
    r = parse_live_text(SAMPLE_MULTILINE)
    assert r.id_number == "042079016888"
    assert r.full_name == "TRẦN THỊ BÌNH"
    assert r.date_of_birth == "1985-05-20"
    assert r.gender == "female"
    assert r.nationality == "Vietnam"
    assert r.place_of_residence is not None


# ── Test 3: Số CCCD 12 chữ số ────────────────────────────────────────────────

def test_id_number_12_digits():
    r = parse_live_text("Số CCCD: 001099012345\nHọ và tên: LÊ MINH TÚ\nNgày sinh: 01/01/2000\nGiới tính: Nam\nQuốc tịch: Việt Nam\nNơi cư trú: Hà Nội")
    assert r.id_number == "001099012345"
    assert len(r.id_number) == 12


# ── Test 4: Số CMND 9 chữ số ─────────────────────────────────────────────────

def test_id_number_9_digits():
    r = parse_live_text("Số CMND: 025678901\nHọ và tên: PHẠM VĂN C\nNgày sinh: 12/12/1975\nGiới tính: Nam\nQuốc tịch: Việt Nam\nNơi cư trú: Đà Nẵng")
    assert r.id_number == "025678901"
    assert len(r.id_number) == 9


# ── Test 5: Giới tính Nữ → female ────────────────────────────────────────────

def test_gender_female():
    r = parse_live_text(
        "Số định danh: 079099001122\n"
        "Họ tên: VÕ THỊ DUNG\n"
        "Ngày sinh: 08/08/1988\n"
        "Giới tính: Nữ\n"
        "Quốc tịch: Việt Nam\n"
        "Nơi cư trú: Cần Thơ"
    )
    assert r.gender == "female"


# ── Test 6: Định dạng ngày khác nhau ─────────────────────────────────────────

@pytest.mark.parametrize("date_str,expected", [
    ("15/03/1990", "1990-03-15"),
    ("15-03-1990", "1990-03-15"),
    ("15.03.1990", "1990-03-15"),
])
def test_date_formats(date_str, expected):
    text = f"Số định danh: 042079012345\nHọ tên: TEST USER\nNgày sinh: {date_str}\nGiới tính: Nam\nQuốc tịch: Việt Nam\nNơi cư trú: Hà Nội"
    r = parse_live_text(text)
    assert r.date_of_birth == expected


# ── Test 7: Text rỗng → parse_status=failed ──────────────────────────────────

def test_empty_text():
    r = parse_live_text("")
    assert r.parse_status == "failed"
    assert len(r.missing_fields) == 6  # tất cả required fields


# ── Test 8: Text không chứa CCCD → partial hoặc failed ───────────────────────

def test_irrelevant_text():
    r = parse_live_text("Hello world. This is some random text.\nNo CCCD data here.")
    assert r.parse_status in ("partial", "failed")
    assert r.id_number is None


# ── Test 9: to_dict() trả về đúng structure ──────────────────────────────────

def test_to_dict_structure():
    r = parse_live_text(SAMPLE_FULL)
    d = r.to_dict()
    required_keys = [
        "id_number", "full_name", "date_of_birth", "gender", "nationality",
        "place_of_residence", "place_of_birth", "issue_date", "expiry_date",
        "raw_text", "source", "kyc_method", "parse_status", "missing_fields",
    ]
    for key in required_keys:
        assert key in d, f"Missing key: {key}"
    assert d["source"] == "vneid_screenshot_live_text"
    assert d["kyc_method"] == "vneid_screenshot_plus_live_text"


# ── Test 10: Thiếu place_of_residence → parse_status=partial ─────────────────

SAMPLE_MISSING_RESIDENCE = """
Số định danh cá nhân: 042079016999
Họ và tên: HOÀNG VĂN E
Ngày sinh: 01/06/1992
Giới tính: Nam
Quốc tịch: Việt Nam
"""

def test_partial_missing_required():
    r = parse_live_text(SAMPLE_MISSING_RESIDENCE)
    assert r.parse_status == "partial"
    assert "Nơi cư trú" in r.missing_fields
    assert r.id_number == "042079016999"
    assert r.full_name == "HOÀNG VĂN E"
