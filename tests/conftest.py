"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.events.base import EventBrand, EventParty, EventSite, EventUser
from byceps.services.brand.models import BrandID
from byceps.services.party.models import PartyID
from byceps.services.site.models import SiteID
from byceps.services.user.models.user import UserID

from tests.helpers import generate_token, generate_uuid


@pytest.fixture(scope='session')
def make_event_brand():
    def _wrapper(
        *,
        id: str | None = None,
        title: str | None = None,
    ) -> EventBrand:
        if id is None:
            id = generate_token()

        if title is None:
            title = generate_token()

        return EventBrand(
            id=BrandID(id),
            title=title,
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_event_party():
    def _wrapper(
        *,
        id: str | None = None,
        title: str | None = None,
    ) -> EventParty:
        if id is None:
            id = generate_token()

        if title is None:
            title = generate_token()

        return EventParty(
            id=PartyID(id),
            title=title,
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_event_site():
    def _wrapper(
        *,
        id: str | None = None,
        title: str | None = None,
    ) -> EventSite:
        if id is None:
            id = generate_token()

        if title is None:
            title = generate_token()

        return EventSite(
            id=SiteID(id),
            title=title,
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_event_user():
    def _wrapper(
        *,
        screen_name: str | None = '__random__',
    ) -> EventUser:
        if screen_name == '__random__':
            screen_name = generate_token()

        return EventUser(
            id=UserID(generate_uuid()),
            screen_name=screen_name,
        )

    return _wrapper
