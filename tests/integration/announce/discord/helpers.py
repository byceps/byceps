"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus

from requests_mock import Mocker


def now() -> datetime:
    return datetime.utcnow()


@contextmanager
def mocked_webhook_receiver(url: str):
    with Mocker() as mock:
        mock.post(url, status_code=HTTPStatus.NO_CONTENT)
        yield mock


def assert_request(mock, expected_content: str) -> None:
    assert mock.called

    history = mock.request_history
    assert len(history) == 1

    actual = mock.last_request.json()

    assert actual == {'content': expected_content}
