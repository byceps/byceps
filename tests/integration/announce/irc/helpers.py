"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager
from datetime import datetime
from typing import List

from requests_mock import Mocker


BOT_URL = 'http://127.0.0.1:12345'

CHANNEL_ORGA_LOG = '#acmeparty-internal-log'
CHANNEL_PUBLIC = '#acmeparty'


def now() -> datetime:
    return datetime.utcnow()


@contextmanager
def mocked_irc_bot():
    with Mocker() as mock:
        mock.post(BOT_URL)
        yield mock


def assert_submitted_data(
    mock, expected_channels: List[str], expected_text: str
) -> None:
    call = get_mock_calls(mock, 1)
    actual = call.json()
    assert_request_data(actual, expected_channels, expected_text)


def assert_request_data(
    actual, expected_channels: List[str], expected_text: str
) -> None:
    assert actual['channels'] == expected_channels
    assert actual['text'] == expected_text

    # Don't allow any other keys.
    assert actual.keys() == {'channels', 'text'}


def get_only_call(mock):
    assert mock.called

    history = mock.request_history
    assert len(history) == 1

    return history[0]
