"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.services.user import command_service as user_command_service
from byceps.services.user_message import service as user_message_service

from tests.helpers import create_user


def test_recipient_formatting(site, params):
    screen_name, email_address, expected = params

    user = create_user(screen_name, email_address=email_address)

    message = user_message_service.create_message(
        user.id, user.id, '', '', site.id
    )

    assert message.recipients == [expected]

    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture(params=[
    ('Alice', 'alice@example.com', 'Alice <alice@example.com>'),
    ('<AngleInvestor>', 'angleinvestor@example.com', '"<AngleInvestor>" <angleinvestor@example.com>'),
    ('-=]YOLO[=-', 'yolo@example.com', '"-=]YOLO[=-" <yolo@example.com>'),
])
def params(request):
    yield request.param
