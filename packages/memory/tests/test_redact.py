"""Redaction: secrets never enter memory."""

from actlet_memory.redact import looks_like_secret_only, redact


def test_openai_key_redacted():
    assert redact("my key is sk-abcdefghij1234567890xyz") == "my key is [REDACTED]"


def test_github_token_redacted():
    assert redact("token ghp_abcdefghij1234567890") == "token [REDACTED]"


def test_password_assignment_redacted():
    assert redact("password: s3cr3t!") == "password=[REDACTED]"


def test_ssn_redacted():
    assert redact("ssn 123-45-6789 here") == "ssn [REDACTED-SSN] here"


def test_card_redacted():
    assert redact("card 4111 1111 1111 1111") == "card [REDACTED-CARD]"


def test_plain_text_untouched():
    text = "Syed prefers morning meetings and drinks chai."
    assert redact(text) == text


def test_secret_only_detected():
    assert looks_like_secret_only("sk-abcdefghij1234567890xyz") is True
    assert looks_like_secret_only("  ghp_abcdefghij1234567890  ") is True
    assert looks_like_secret_only("remember my password") is False
