"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.services.site import service as site_service
from byceps.services.user import command_service as user_command_service
from byceps.services.user_message import service as user_message_service

from tests.conftest import database_recreated
from tests.helpers import create_site, create_user


@pytest.fixture(scope='module')
def app(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            yield party_app


@pytest.fixture(scope='module')
def site(app, make_email_config):
    make_email_config()
    site = create_site()
    yield site
    site_service.delete_site(site.id)


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
