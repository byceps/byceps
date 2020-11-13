"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.news import channel_service, service as item_service

from tests.helpers import login_user


@pytest.fixture(scope='package')
def news_admin(make_admin):
    permission_ids = {
        'admin.access',
        'news_channel.create',
        'news_item.create',
        'news_item.publish',
        'news_item.update',
        'news_item.view',
        'news_item.view_draft',
    }
    admin = make_admin('NewsAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def news_admin_client(make_client, admin_app, news_admin):
    return make_client(admin_app, user_id=news_admin.id)


@pytest.fixture()
def channel(brand):
    channel = channel_service.create_channel(
        brand.id, 'test-channel-1', 'https://newssite.example/posts/'
    )

    yield channel

    channel_service.delete_channel(channel.id)


@pytest.fixture()
def item(channel, news_admin):
    item = item_service.create_item(
        channel.id,
        'save-the-date',
        news_admin.id,
        'Save the Date!',
        'Party will be next year.',
    )

    yield item

    item_service.delete_item(item.id)
