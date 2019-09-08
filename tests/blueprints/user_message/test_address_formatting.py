"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.services.user_message import service as user_message_service

from tests.conftest import database_recreated
from tests.helpers import app_context, create_brand, create_email_config, \
    create_party, create_site, create_user


def test_recipient_formatting(site, params):
    screen_name, email_address, expected = params

    user = create_user(screen_name, email_address=email_address)

    message = user_message_service.create_message(user.id, user.id, '', '',
                                                  site.id)

    assert message.recipients == [expected]


@pytest.fixture(params=[
    ('Alice', 'alice@example.com', 'Alice <alice@example.com>'),
    ('<AngleInvestor>', 'angleinvestor@example.com', '"<AngleInvestor>" <angleinvestor@example.com>'),
    ('-=]YOLO[=-', 'yolo@example.com', '"-=]YOLO[=-" <yolo@example.com>'),
])
def params(request):
    yield request.param


@pytest.fixture(scope='module')
def site(db):
    with app_context():
        with database_recreated(db):
            create_email_config()

            brand = create_brand()
            party = create_party(brand.id)

            site = create_site(party.id)

            yield site
