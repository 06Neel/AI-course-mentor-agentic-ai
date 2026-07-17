import re


class SecurityManager:
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?prior\s+instructions",
        r"disregard\s+(all\s+)?previous",
        r"you\s+are\s+now\s+",
        r"act\s+as\s+if\s+",
        r"pretend\s+you\s+are\s+",
        r"roleplay\s+as\s+",
        r"system\s*:\s*",
        r"admin\s*:\s*",
        r"override\s+",
        r"bypass\s+",
        r"jailbreak",
        r"DAN\s+mode",
        r"do\s+anything\s+now",
    ]

    SENSITIVE_PATTERNS = [
        r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # credit card
        r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",   # SSN
        r"password\s*[:=]\s*\S+",
        r"api[_\s]?key\s*[:=]\s*\S+",
        r"secret\s*[:=]\s*\S+",
    ]

    MAX_INPUT_LENGTH = 5000

    @classmethod
    def check_injection(cls, text: str) -> tuple[bool, str]:
        text_lower = text.lower()
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return True, "Potential prompt injection detected"
        return False, "Safe"

    @classmethod
    def check_sensitive(cls, text: str) -> tuple[bool, str]:
        for pattern in cls.SENSITIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "Potentially sensitive content detected"
        return False, "Safe"

    @classmethod
    def validate_input(cls, text: str) -> tuple[bool, str]:
        if not text or not text.strip():
            return False, "Empty input"

        if len(text) > cls.MAX_INPUT_LENGTH:
            return False, f"Input too long ({len(text)} chars). Max: {cls.MAX_INPUT_LENGTH}"

        injection_detected, injection_msg = cls.check_injection(text)
        if injection_detected:
            return False, injection_msg

        return True, "Valid"

    @classmethod
    def sanitize(cls, text: str) -> str:
        text = text.strip()
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        return text
