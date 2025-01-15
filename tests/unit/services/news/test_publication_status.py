"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta

from freezegun import freeze_time
import pytest

from byceps.services.news.models import (
    BodyFormat,
    NewsChannel,
    NewsChannelID,
    NewsItem,
    NewsItemID,
    PublicationStatus,
    PublicationStatusDraft,
    PublicationStatusPublished,
    PublicationStatusScheduledForPublication,
)

from tests.helpers import generate_token, generate_uuid


DATETIME_NOW = datetime.utcnow()
DATETIME_FUTURE = DATETIME_NOW + timedelta(days=1)
DATETIME_PAST = DATETIME_NOW - timedelta(days=1)


@pytest.mark.parametrize(
    ('published_at', 'expected'),
    [
        (None, PublicationStatusDraft()),
        (DATETIME_PAST, PublicationStatusPublished()),
        (DATETIME_FUTURE, PublicationStatusScheduledForPublication()),
    ],
)
def test_publication_status(
    make_item,
    published_at: datetime | None,
    expected: PublicationStatus,
):
    with freeze_time(DATETIME_NOW):
        item = make_item(published_at=published_at)
        assert item.publication_status == expected


@pytest.mark.parametrize(
    ('published_at', 'expected'),
    [
        (None, 'draft'),
        (DATETIME_PAST, 'published'),
        (DATETIME_FUTURE, 'scheduled_for_publication'),
    ],
)
def test_publication_status_name(
    make_item,
    published_at: datetime | None,
    expected: str,
):
    with freeze_time(DATETIME_NOW):
        item = make_item(published_at=published_at)
        assert item.publication_status_name == expected


@pytest.fixture()
def channel(brand) -> NewsChannel:
    return NewsChannel(
        id=NewsChannelID(generate_token()),
        brand_id=brand.id,
        announcement_site_id=None,
        archived=False,
    )


@pytest.fixture()
def make_item(channel: NewsChannel):
    def _wrapper(published_at: datetime | None) -> NewsItem:
        token = generate_token()

        return NewsItem(
            id=NewsItemID(generate_uuid()),
            brand_id=channel.brand_id,
            channel=channel,
            slug=token,
            published_at=published_at,
            published=(published_at is not None)
            and (published_at >= datetime.utcnow()),
            title=token,
            body=token,
            body_format=BodyFormat.markdown,
            images=[],
            featured_image=None,
        )

    return _wrapper
