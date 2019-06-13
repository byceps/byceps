"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.database import db
from byceps.services.email.models import EmailConfig
from byceps.services.user_message import service as user_message_service

from testfixtures.brand import create_brand as _create_brand

from tests.helpers import app_context, create_user


def test_recipient_formatting(application, params):
    screen_name, email_address, expected = params

    brand = create_brand()

    user = create_user(screen_name, email_address=email_address)

    message = user_message_service.create_message(user.id, user.id, '', '', brand.id)

    assert message.recipients == [expected]


@pytest.fixture(params=[
    ('Alice', 'alice@example.com', 'Alice <alice@example.com>'),
    ('<AngleInvestor>', 'angleinvestor@example.com', '"<AngleInvestor>" <angleinvestor@example.com>'),
    ('-=]YOLO[=-', 'yolo@example.com', '"-=]YOLO[=-" <yolo@example.com>'),
])
def params(request):
    yield request.param


@pytest.fixture
def application():
    with app_context():
        set_up_database()

        yield

        tear_down_database()


# helpers


def set_up_database():
    db.reflect()
    db.drop_all()
    db.create_all()


def tear_down_database():
    db.session.remove()
    db.drop_all()


def create_brand():
    brand = _create_brand()
    db.session.add(brand)
    db.session.commit()

    sender_address = '{}@example.com'.format(brand.id)
    email_config = EmailConfig(brand.id, sender_address)
    db.session.add(email_config)
    db.session.commit()

    return brand
