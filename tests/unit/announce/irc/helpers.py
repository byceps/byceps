"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.webhooks.models import AnnouncementRequest


def now() -> datetime:
    return datetime.utcnow()


def build_announcement_request_for_irc(text: str) -> AnnouncementRequest:
    return AnnouncementRequest(
        url='http://127.0.0.1:12345/',
        data={'channel': '#eventlog', 'text': text},
    )
