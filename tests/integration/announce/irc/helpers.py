"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus

from requests_mock import Mocker


BOT_URL = 'http://127.0.0.1:12345'

CHANNEL_INTERNAL = '#acmeparty-internal-log'
CHANNEL_PUBLIC = '#acmeparty'


def now() -> datetime:
    return datetime.utcnow()


@contextmanager
def mocked_irc_bot():
    with Mocker() as mock:
        mock.post(BOT_URL, status_code=HTTPStatus.ACCEPTED)
        yield mock


def assert_submitted_data(
    mock, expected_channel: str, expected_text: str
) -> None:
    actual = get_submitted_json(mock, 1)[0]
    assert_request_data(actual, expected_channel, expected_text)


def assert_request_data(
    actual, expected_channel: str, expected_text: str
) -> None:
    assert actual['channel'] == expected_channel
    assert actual['text'] == expected_text

    # Don't allow any other keys.
    assert actual.keys() == {'channel', 'text'}


def get_submitted_json(mock, expected_call_count: int) -> list[str]:
    assert mock.called

    history = mock.request_history
    assert len(history) == expected_call_count

    requests = history[:expected_call_count]
    return [req.json() for req in requests]
