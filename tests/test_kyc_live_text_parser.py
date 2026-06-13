"""Unit tests cho kyc_live_text_parser.

Run: python -m pytest tests/test_kyc_live_text_parser.py -v
"""
import pytest
from backend.services.kyc_live_text_parser import (
    parse_cccd_live_text,
    is_cccd_text,
    REQUIRED_FIELDS,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_FULL = """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
CĂN CƯỚC
Số định danh cá nhân / Personal Identification number:
042079016888
Họ, chữ đệm và tên / Full name:
TRẦN XUÂN LINH
Ngày, tháng, năm sinh / Date of birth:
20/01/1979
Giới tính / Sex: Nam
Quốc tịch / Nationality: Việt Nam
Nơi cư trú / Place of residence:
P711-NO1C Golden Land 275 Nguyễn Trãi, TXT, Thanh Xuân, Hà Nội
Nơi đăng ký khai sinh / Place of birth:
Tân Dân, Đức Thọ, Hà Tĩnh
Ngày, tháng, năm cấp / Date of issue:
31/10/2024
Ngày, tháng, năm hết hạn / Date of Expiry:
20/01/2039"""


# ── Test 1: Input chuẩn — đầy đủ mọi trường ─────────────────────────────────

def test_full_input():
    r = parse_cccd_live_text(SAMPLE_FULL)

    assert r["id_number"]          == "042079016888"
    assert r["full_name"]          == "TRẦN XUÂN LINH"
    assert r["date_of_birth"]      == "1979-01-20"
    assert r["gender"]             == "male"
    assert r["nationality"]        == "Vietnam"
    assert "Nguyễn Trãi"           in r["place_of_residence"]
    assert "Đức Thọ"               in r["place_of_birth"]
    assert r["issue_date"]         == "2024-10-31"
    assert r["expiry_date"]        == "2039-01-20"
    assert r["source"]             == "iphone_live_text"
    assert r["parse_status"]       == "success"
    assert r["missing_fields"]     == []
    assert SAMPLE_FULL             in r["raw_text"]


# ── Test 2: Label và value cùng dòng ─────────────────────────────────────────

SAMPLE_INLINE = """CĂN CƯỚC CÔNG DÂN
Số định danh cá nhân: 079099001234
Họ và tên: NGUYỄN VĂN AN
Ngày sinh: 15/03/1990
Giới tính: Nam
Quốc tịch: Việt Nam
Nơi cư trú: 12 Lê Lợi, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh
Nơi khai sinh: Bình Thạnh, TP. Hồ Chí Minh
Ngày cấp: 20/08/2023
Hết hạn: 15/03/2035"""

def test_label_value_same_line():
    r = parse_cccd_live_text(SAMPLE_INLINE)

    assert r["id_number"]      == "079099001234"
    assert r["full_name"]      == "NGUYỄN VĂN AN"
    assert r["date_of_birth"]  == "1990-03-15"
    assert r["gender"]         == "male"
    assert r["nationality"]    == "Vietnam"
    assert "Lê Lợi"            in r["place_of_residence"]
    assert r["parse_status"]   == "success"


# ── Test 3: Label và value khác dòng ─────────────────────────────────────────

SAMPLE_MULTILINE = """CĂN CƯỚC
Số định danh cá nhân
042079055555
Họ, chữ đệm và tên
PHẠM THỊ BÌNH
Ngày, tháng, năm sinh
08/08/1988
Giới tính
Nữ
Quốc tịch
Việt Nam
Nơi cư trú
123 Trần Hưng Đạo, Quận 5, TP.HCM
Nơi đăng ký khai sinh
Bình Định
Ngày, tháng, năm cấp
01/01/2024
Ngày, tháng, năm hết hạn
08/08/2038"""

def test_label_value_different_lines():
    r = parse_cccd_live_text(SAMPLE_MULTILINE)

    assert r["id_number"]      == "042079055555"
    assert r["full_name"]      == "PHẠM THỊ BÌNH"
    assert r["date_of_birth"]  == "1988-08-08"
    assert r["gender"]         == "female"
    assert r["nationality"]    == "Vietnam"
    assert r["parse_status"]   == "success"


# ── Test 4: Thiếu ngày hết hạn — vẫn thành công ──────────────────────────────

SAMPLE_NO_EXPIRY = """CĂN CƯỚC
Số định danh cá nhân: 001099012345
Họ và tên: LÊ MINH TÚ
Ngày sinh: 01/06/1992
Giới tính: Nam
Quốc tịch: Việt Nam
Nơi cư trú: Phú Thọ, Hà Nội
Nơi khai sinh: Hà Tĩnh
Ngày cấp: 15/07/2023"""

def test_missing_expiry_date():
    r = parse_cccd_live_text(SAMPLE_NO_EXPIRY)

    assert r["parse_status"]   == "success"   # expiry_date không bắt buộc
    assert r["missing_fields"] == []
    assert r["expiry_date"]    is None
    assert r["issue_date"]     == "2023-07-15"


# ── Test 5: Thiếu địa chỉ cư trú — trả về partial ────────────────────────────

SAMPLE_NO_RESIDENCE = """CĂN CƯỚC
Số định danh cá nhân: 042079016001
Họ và tên: VÕ THỊ DUNG
Ngày sinh: 12/12/1985
Giới tính: Nữ
Quốc tịch: Việt Nam"""

def test_missing_place_of_residence():
    r = parse_cccd_live_text(SAMPLE_NO_RESIDENCE)

    assert r["parse_status"]    == "partial"
    assert "Nơi cư trú"         in r["missing_fields"]
    assert r["id_number"]       == "042079016001"
    assert r["full_name"]       == "VÕ THỊ DUNG"
    assert r["place_of_residence"] is None


# ── Test 6: Số CCCD không đủ 12 chữ số → id_number = None ───────────────────

def test_invalid_id_number():
    text = """CĂN CƯỚC
Số định danh: 04207901
Họ và tên: TEST USER
Ngày sinh: 01/01/2000
Giới tính: Nam
Nơi cư trú: Hà Nội"""

    r = parse_cccd_live_text(text)

    assert r["id_number"]   is None
    assert r["parse_status"] in ("partial", "failed")
    assert "Số định danh"   in r["missing_fields"]


# ── Test 7: Text rỗng → failed ───────────────────────────────────────────────

def test_empty_text():
    r = parse_cccd_live_text("")

    assert r["parse_status"]   == "failed"
    assert len(r["missing_fields"]) == len(REQUIRED_FIELDS)


# ── Test 8: Text không phải CCCD → failed ────────────────────────────────────

def test_irrelevant_text():
    r = parse_cccd_live_text("Xin chào! Đây là tin nhắn bình thường không có dữ liệu CCCD.")

    assert r["parse_status"]   in ("partial", "failed")
    assert r["id_number"]      is None
    assert r["full_name"]      is None


# ── Test 9: is_cccd_text() nhận diện đúng trigger ────────────────────────────

@pytest.mark.parametrize("text,expected", [
    ("Số định danh cá nhân: 042079016888",    True),
    ("CĂN CƯỚC\nSố định danh: 123",           True),
    ("CCCD của tôi là 042079016888",           True),
    ("Cộng hòa xã hội chủ nghĩa Việt Nam",    True),
    ("Personal Identification number: 042",   True),
    ("Xin chào, bạn khỏe không?",             False),
    ("",                                       False),
])
def test_is_cccd_text(text, expected):
    assert is_cccd_text(text) is expected


# ── Test 10: Song ngữ VI/EN — trích xuất đúng trường ─────────────────────────

SAMPLE_BILINGUAL = """SOCIALIST REPUBLIC OF VIETNAM
IDENTITY CARD
Personal Identification number:
042079016999
Full name:
HOÀNG VĂN E
Date of birth: 25/12/1995
Sex: Nam
Nationality: Việt Nam
Place of residence:
88 Đinh Tiên Hoàng, Bình Thạnh, TP.HCM
Place of birth: Nghệ An
Date of issue: 10/05/2022
Date of Expiry: 25/12/2037"""

def test_bilingual_english_labels():
    r = parse_cccd_live_text(SAMPLE_BILINGUAL)

    assert r["id_number"]      == "042079016999"
    assert r["full_name"]      == "HOÀNG VĂN E"
    assert r["date_of_birth"]  == "1995-12-25"
    assert r["gender"]         == "male"
    assert r["nationality"]    == "Vietnam"
    assert "Đinh Tiên Hoàng"   in r["place_of_residence"]
    assert r["place_of_birth"] is not None
    assert r["issue_date"]     == "2022-05-10"
    assert r["expiry_date"]    == "2037-12-25"
    assert r["parse_status"]   == "success"
