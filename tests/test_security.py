import pytest
from backend.security.password import hash_password, verify_password, generate_temp_password, generate_user_code
from backend.security.totp import generate_totp_secret, verify_totp, generate_recovery_codes
from backend.security.jwt import create_access_token, decode_token


def test_password_hash_and_verify():
    pw = "MyPassword123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password("wrong", hashed)


def test_temp_password_complexity():
    for _ in range(10):
        pw = generate_temp_password()
        assert len(pw) >= 8
        assert any(c.isupper() for c in pw)
        assert any(c.islower() for c in pw)
        assert any(c.isdigit() for c in pw)


def test_user_code_format():
    code = generate_user_code()
    assert code.startswith("USR")
    assert len(code) > 3


def test_totp_verify():
    secret = generate_totp_secret()
    import pyotp
    totp = pyotp.TOTP(secret)
    current_code = totp.now()
    assert verify_totp(secret, current_code)
    assert not verify_totp(secret, "000000")


def test_recovery_codes():
    codes = generate_recovery_codes(8)
    assert len(codes) == 8
    assert all(len(c) == 10 for c in codes)


def test_jwt_create_and_decode():
    token = create_access_token("user-123", extra={"role": "USER"})
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "USER"
    assert payload["type"] == "access"


def test_jwt_invalid_token():
    with pytest.raises(ValueError):
        decode_token("invalid.token.here")
