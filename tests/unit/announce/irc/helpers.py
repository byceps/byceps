"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any

from byceps.services.webhooks.models import AnnouncementRequest


def assert_text(actual: AnnouncementRequest | None, expected_text: str) -> None:
    assert actual is not None

    # Separate assertion function with its own `actual` variable is a
    # workaround to make pytest show only the relevant value instead of
    # the full `actual` object on assertion failure.

    _assert(set(actual.data.keys()), {'channel', 'text'})
    _assert(actual.data['channel'], '#eventlog')
    _assert(actual.data['text'], expected_text)


def _assert(actual: Any, expected: Any) -> None:
    assert actual == expected
