"""
byceps.scripts.validators
~~~~~~~~~~~~~~~~~~~~~~~~~

Validators for use with Click_.

.. _Click: http://click.pocoo.org/

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.brand.transfer.models import Brand
from byceps.services.brand import service as brand_service
from byceps.services.party.transfer.models import Party
from byceps.services.party import service as party_service
from byceps.services.site.transfer.models import Site, SiteID
from byceps.services.site import service as site_service
from byceps.services.user.models.user import User as DbUser
from byceps.services.user import service as user_service
from byceps.services.user.transfer.models import User
from byceps.typing import BrandID, PartyID, UserID


def validate_brand(ctx, param, brand_id: BrandID) -> Brand:
    brand = brand_service.find_brand(brand_id)

    if not brand:
        raise click.BadParameter(f'Unknown brand ID "{brand_id}".')

    return brand


def validate_party(ctx, param, party_id: PartyID) -> Party:
    party = party_service.find_party(party_id)

    if not party:
        raise click.BadParameter(f'Unknown party ID "{party_id}".')

    return party


def validate_site(ctx, param, site_id: SiteID) -> Site:
    site = site_service.find_site(site_id)

    if not site:
        raise click.BadParameter(f'Unknown site ID "{site_id}".')

    return site


def validate_user_id(ctx, param, user_id: UserID) -> User:
    user = user_service.find_user(user_id)

    if not user:
        raise click.BadParameter(f'Unknown user ID "{user_id}".')

    return user


def validate_user_screen_name(ctx, param, screen_name: str) -> DbUser:
    user = user_service.find_user_by_screen_name(screen_name)

    if not user:
        raise click.BadParameter(f'Unknown user screen name "{screen_name}".')

    return user
