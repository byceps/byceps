"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus

from requests_mock import Mocker


BOT_URL = 'http://127.0.0.1:12345'


def now() -> datetime:
    return datetime.utcnow()


@contextmanager
def mocked_irc_bot():
    with Mocker() as mock:
        mock.post(BOT_URL, status_code=HTTPStatus.ACCEPTED)
        yield mock


def assert_submitted_data(mock, expected_text: str) -> None:
    assert mock.call_count == 1
    actual = mock.last_request.json()
    assert actual['text'] == expected_text
