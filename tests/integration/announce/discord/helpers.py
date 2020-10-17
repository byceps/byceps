"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

from requests_mock import Mocker


@contextmanager
def mocked_webhook_receiver(url: str):
    with Mocker() as mock:
        mock.post(url)
        yield mock


def assert_request(mock, expected_content: str) -> None:
    assert mock.called

    history = mock.request_history
    assert len(history) == 1

    actual = mock.last_request.json()

    assert actual == {'content': expected_content}
