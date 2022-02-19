"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

import pytest

from byceps.services.brand.transfer.models import Brand
from byceps.services.news import channel_service, service as item_service
from byceps.services.news.transfer.models import BodyFormat, Channel, ChannelID

from tests.helpers import generate_token, log_in_user


@pytest.fixture(scope='package')
def news_admin(make_admin):
    permission_ids = {
        'admin.access',
        'news_channel.administrate',
        'news_item.create',
        'news_item.publish',
        'news_item.update',
        'news_item.view',
        'news_item.view_draft',
    }
    admin = make_admin('NewsAdmin', permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def news_admin_client(make_client, admin_app, news_admin):
    return make_client(admin_app, user_id=news_admin.id)


@pytest.fixture
def make_channel(brand: Brand):
    def _wrapper(channel_id: Optional[ChannelID] = None) -> Channel:
        if channel_id is None:
            channel_id = ChannelID(generate_token())

        return channel_service.create_channel(
            brand.id, channel_id, 'https://newssite.example/posts/'
        )

    return _wrapper


@pytest.fixture
def channel(make_channel):
    return make_channel()


@pytest.fixture
def item(channel, news_admin):
    return item_service.create_item(
        channel.id,
        f'save-the-date-{generate_token()}',
        news_admin.id,
        'Save the Date!',
        'Party will be next year.',
        BodyFormat.html,
    )
