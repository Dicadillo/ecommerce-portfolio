from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


def generate_unique_username(prefix: str = "robot") -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:6]
    return f"{prefix}_{timestamp}_{suffix}"


def generate_unique_email(prefix: str = "robot") -> str:
    username = generate_unique_username(prefix)
    return f"{username}@example.com"


VALID_PASSWORD = "RobotTest123!"
APPROVED_CARD = "4111111111111111"
REJECTED_CARD = "4000000000000002"