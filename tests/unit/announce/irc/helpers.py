"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.services.webhooks.models import AnnouncementRequest


def now() -> datetime:
    return datetime.utcnow()


def assert_text(actual: AnnouncementRequest | None, expected_text: str) -> None:
    assert actual is not None
    assert actual.data == {'channel': '#eventlog', 'text': expected_text}
