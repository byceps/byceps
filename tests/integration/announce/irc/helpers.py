"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from typing import Any

from requests_mock import Mocker


BOT_URL = 'http://127.0.0.1:12345'


def now() -> datetime:
    return datetime.utcnow()


@contextmanager
def mocked_irc_bot():
    with Mocker() as mock:
        mock.post(BOT_URL, status_code=HTTPStatus.ACCEPTED)
        yield mock


def assert_submitted_text(mock, expected_text: str) -> None:
    expected = {'text': expected_text}
    assert_submitted_data(mock, expected)


def assert_submitted_data(mock, expected: dict[str, Any]) -> None:
    assert mock.call_count == 1
    actual = mock.last_request.json()
    for expected_key, expected_value in expected.items():
        assert actual[expected_key] == expected_value
