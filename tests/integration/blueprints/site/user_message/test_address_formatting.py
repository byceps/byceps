"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

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
    ('Alicia', 'alicia@users.test', 'Alicia <alicia@users.test>'),
    ('<AngleInvestor>', 'angleinvestor@users.test', '"<AngleInvestor>" <angleinvestor@users.test>'),
    ('-=]YOLO[=-', 'yolo@users.test', '"-=]YOLO[=-" <yolo@users.test>'),
])
def params(request):
    yield request.param
