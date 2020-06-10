"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.services.user_message import service as user_message_service


def test_recipient_formatting(make_user, site, params):
    screen_name, email_address, expected = params

    user = make_user(screen_name, email_address=email_address)

    message = user_message_service.create_message(
        user.id, user.id, '', '', site.id
    )

    assert message.recipients == [expected]


@pytest.fixture(params=[
    ('Alice', 'alice@users.test', 'Alice <alice@users.test>'),
    ('<AngleInvestor>', 'angleinvestor@users.test', '"<AngleInvestor>" <angleinvestor@users.test>'),
    ('-=]YOLO[=-', 'yolo@users.test', '"-=]YOLO[=-" <yolo@users.test>'),
])
def params(request):
    yield request.param
