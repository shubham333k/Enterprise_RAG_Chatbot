"""
PII masking utilities.
Masks common PII patterns (email, phone, SSN, Aadhaar)
from document text before indexing or from answers before returning.
"""
import re



# ─── Regex patterns ────────────────────────────────────────────────────────────
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'(\+?\d[\d\s\-().]{7,}\d)')
SSN_PATTERN = re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b')
AADHAAR_PATTERN = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')
CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d[ \-]?){13,16}\b')


def mask_pii(text: str, replacement: str = "[REDACTED]") -> str:
    """
    Replace common PII patterns with a placeholder.
    Applied selectively — use only on fields where PII is expected.
    """
    text = EMAIL_PATTERN.sub("[EMAIL REDACTED]", text)
    text = SSN_PATTERN.sub("[SSN REDACTED]", text)
    text = AADHAAR_PATTERN.sub("[ID REDACTED]", text)
    text = CREDIT_CARD_PATTERN.sub("[CARD REDACTED]", text)
    # Phone last (broad pattern, higher false positive risk)
    text = PHONE_PATTERN.sub("[PHONE REDACTED]", text)
    return text


def has_pii(text: str) -> bool:
    """Return True if text likely contains PII."""
    return any([
        EMAIL_PATTERN.search(text),
        SSN_PATTERN.search(text),
        AADHAAR_PATTERN.search(text),
    ])
