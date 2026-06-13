"""Giải mã QR Code từ ảnh VNeID. Không dùng OCR.

VNeID QR (CCCD chip 2021+) — format pipe-separated 7+ trường:
  {id_number}|{old_id}|{full_name}|{dob_ddmmyyyy}|{gender}|{address}|{expiry_ddmmyyyy}

Chiến lược decode (theo thứ tự):
  1. OpenCV QRCodeDetectorAruco   — tốt nhất cho ảnh nén/nhỏ
  2. OpenCV QRCodeDetector        — fallback
  3. pyzbar trên nhiều biến thể   — last resort
"""
from __future__ import annotations

import io
import logging
import re
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from pyzbar import pyzbar

logger = logging.getLogger(__name__)


def decode_qr_from_image(image_bytes: bytes) -> Optional[dict]:
    """Đọc QR Code từ image bytes.

    Returns dict: cccd, full_name, date_of_birth (YYYY-MM-DD), gender, raw_qr
    hoặc None nếu không đọc được.
    """
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        logger.warning("qr_decode: cannot open image — %s", exc)
        return None

    w, h = pil_img.size
    logger.info("qr_decode: image size=%dx%d", w, h)

    # ── 1. OpenCV Aruco QR detector (tốt nhất) ────────────────────────────────
    cv_img = _pil_to_cv(pil_img)
    result = _try_opencv_aruco(cv_img)
    if result:
        return result

    result = _try_opencv_aruco(_cv_upscale(cv_img, 2))
    if result:
        return result

    result = _try_opencv_aruco(_cv_upscale(cv_img, 3))
    if result:
        return result

    # ── 2. OpenCV standard QRCodeDetector ────────────────────────────────────
    result = _try_opencv_standard(cv_img)
    if result:
        return result

    # Thử thêm với ảnh đã enhance
    for cv_variant in _cv_variants(cv_img):
        result = _try_opencv_aruco(cv_variant)
        if result:
            return result
        result = _try_opencv_standard(cv_variant)
        if result:
            return result

    # ── 3. pyzbar fallback (nhiều biến thể PIL) ───────────────────────────────
    for name, pil_variant in _pil_variants(pil_img):
        codes = pyzbar.decode(pil_variant)
        for code in codes:
            logger.debug("qr_decode: pyzbar type=%s variant=%s", code.type, name)
            try:
                raw = code.data.decode("utf-8")
            except Exception:
                try:
                    raw = code.data.decode("latin-1")
                except Exception:
                    continue
            parsed = _parse_cccd_qr(raw)
            if parsed:
                parsed["raw_qr"] = raw
                logger.info("qr_decode: pyzbar OK variant=%s cccd=****%s", name, parsed["cccd"][-4:])
                return parsed
            if code.type == "QRCODE":
                logger.info("qr_decode: pyzbar non-CCCD QR variant=%s raw=%.80s", name, raw)

    logger.warning("qr_decode: all strategies failed for image %dx%d", w, h)
    return None


# ── OpenCV helpers ─────────────────────────────────────────────────────────────

def _pil_to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _cv_upscale(img: np.ndarray, scale: int) -> np.ndarray:
    h, w = img.shape[:2]
    return cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)


def _try_opencv_aruco(img: np.ndarray) -> Optional[dict]:
    """OpenCV QRCodeDetectorAruco — tốt hơn cho QR nhỏ/mờ."""
    try:
        detector = cv2.QRCodeDetectorAruco()
        data, _, _ = detector.detectAndDecode(img)
        if data:
            logger.info("qr_decode: aruco found raw=%.80s", data)
            parsed = _parse_cccd_qr(data)
            if parsed:
                parsed["raw_qr"] = data
                logger.info("qr_decode: aruco OK cccd=****%s", parsed["cccd"][-4:])
                return parsed
    except Exception as exc:
        logger.debug("qr_decode: aruco error=%s", exc)
    return None


def _try_opencv_standard(img: np.ndarray) -> Optional[dict]:
    """OpenCV QRCodeDetector chuẩn."""
    try:
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        if data:
            logger.info("qr_decode: cv2std found raw=%.80s", data)
            parsed = _parse_cccd_qr(data)
            if parsed:
                parsed["raw_qr"] = data
                logger.info("qr_decode: cv2std OK cccd=****%s", parsed["cccd"][-4:])
                return parsed
    except Exception as exc:
        logger.debug("qr_decode: cv2std error=%s", exc)
    return None


def _cv_variants(img: np.ndarray):
    """Các biến thể OpenCV để thử."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # CLAHE — adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    # Threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Sharpen kernel
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(img, -1, kernel)

    variants = [
        cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR),
        sharpened,
        _cv_upscale(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), 2),
        _cv_upscale(cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2BGR), 2),
        _cv_upscale(cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR), 2),
    ]
    # Crop vùng dưới (VNeID để QR ở phần dưới màn hình)
    h, w = img.shape[:2]
    for crop in [
        img[h // 2:, :],          # bottom half
        img[h // 3:, :],          # bottom 2/3
        img[:, w // 4: 3*w // 4], # center strip
        img[h // 4: 3*h // 4, :], # middle rows
    ]:
        if crop.size > 0:
            variants.append(crop)
            variants.append(_cv_upscale(crop, 2))

    return variants


# ── PIL helpers ────────────────────────────────────────────────────────────────

def _pil_variants(img: Image.Image):
    """Danh sách biến thể PIL để pyzbar thử."""
    w, h = img.size
    gray = img.convert("L")
    variants = [
        ("gray",           gray),
        ("gray_c3",        ImageEnhance.Contrast(gray).enhance(3.0)),
        ("sharp",          img.filter(ImageFilter.SHARPEN)),
        ("inverted",       ImageOps.invert(gray)),
        ("binary128",      gray.point(lambda x: 255 if x > 128 else 0)),
        ("binary160",      gray.point(lambda x: 255 if x > 160 else 0)),
        ("binary96",       gray.point(lambda x: 255 if x > 96  else 0)),
        ("up2",            img.resize((w*2, h*2), Image.LANCZOS)),
        ("up2_gray",       img.resize((w*2, h*2), Image.LANCZOS).convert("L")),
        ("up2_c3",         ImageEnhance.Contrast(
                               img.resize((w*2, h*2), Image.LANCZOS).convert("L")
                           ).enhance(3.0)),
        ("up3_gray",       img.resize((w*3, h*3), Image.LANCZOS).convert("L")),
        ("bottom_half",    gray.crop((0, h//2, w, h))),
        ("bottom_half_up2",gray.crop((0, h//2, w, h)).resize((w*2, h), Image.LANCZOS)),
        ("bottom_third",   gray.crop((0, 2*h//3, w, h))),
        ("top_half",       gray.crop((0, 0, w, h//2))),
    ]
    return variants


# ── CCCD QR parser ─────────────────────────────────────────────────────────────

def _parse_cccd_qr(data: str) -> Optional[dict]:
    """Parse QR text CCCD Việt Nam (7+ trường, phân cách |)."""
    if not data:
        return None
    parts = [p.strip() for p in data.split("|")]
    if len(parts) < 7:
        return None

    id_number  = parts[0]
    full_name  = parts[2]
    dob_raw    = parts[3]
    gender_raw = parts[4]

    if not re.fullmatch(r"\d{9}|\d{12}", id_number):
        return None

    dob = _norm_dob(dob_raw)
    if not dob:
        return None

    return {
        "cccd":          id_number,
        "full_name":     full_name.upper(),
        "date_of_birth": dob,
        "gender":        _norm_gender(gender_raw),
    }


def _norm_dob(raw: str) -> Optional[str]:
    raw = raw.strip()
    if re.fullmatch(r"\d{8}", raw):
        return f"{raw[4:]}-{raw[2:4]}-{raw[:2]}"
    m = re.fullmatch(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", raw)
    if m:
        return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    return None


def _norm_gender(raw: str) -> str:
    r = raw.strip().lower()
    if r in ("nam", "male", "m", "1"):
        return "male"
    if r in ("nữ", "nu", "nư", "female", "f", "0"):
        return "female"
    return r
