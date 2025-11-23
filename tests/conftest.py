"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.brand.models import BrandID
from byceps.services.core.events import EventBrand, EventParty, EventSite
from byceps.services.party.models import PartyID
from byceps.services.site.models import SiteID

from tests.helpers import generate_token


@pytest.fixture(scope='session')
def make_event_brand():
    def _wrapper(
        *,
        brand_id: str | None = None,
        title: str | None = None,
    ) -> EventBrand:
        if brand_id is None:
            brand_id = generate_token()

        if title is None:
            title = generate_token()

        return EventBrand(
            id=BrandID(brand_id),
            title=title,
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_event_party():
    def _wrapper(
        *,
        party_id: str | None = None,
        title: str | None = None,
    ) -> EventParty:
        if party_id is None:
            party_id = generate_token()

        if title is None:
            title = generate_token()

        return EventParty(
            id=PartyID(party_id),
            title=title,
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_event_site():
    def _wrapper(
        *,
        site_id: str | None = None,
        title: str | None = None,
    ) -> EventSite:
        if site_id is None:
            site_id = generate_token()

        if title is None:
            title = generate_token()

        return EventSite(
            id=SiteID(site_id),
            title=title,
        )

    return _wrapper
