"""
bootstrap.validators
~~~~~~~~~~~~~~~~~~~~

Validators for use with Click_.

.. _Click: http://click.pocoo.org/

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.brand.models.brand import Brand
from byceps.services.brand import service as brand_service
from byceps.services.party.models.party import Party
from byceps.services.party import service as party_service
from byceps.services.user.models.user import User
from byceps.services.user import service as user_service
from byceps.typing import BrandID, PartyID, UserID


def validate_brand(ctx, param, brand_id: BrandID) -> Brand:
    brand = brand_service.find_brand(brand_id)

    if not brand:
        raise click.BadParameter('Unknown brand ID "{}".'.format(brand_id))

    return brand


def validate_party(ctx, param, party_id: PartyID) -> Party:
    party = party_service.find_party(party_id)

    if not party:
        raise click.BadParameter('Unknown party ID "{}".'.format(party_id))

    return party


def validate_user_id(ctx, param, user_id: UserID) -> User:
    user = user_service.find_user(user_id)

    if not user:
        raise click.BadParameter('Unknown user ID "{}".'.format(user_id))

    return user


def validate_user_screen_name(ctx, param, screen_name: str) -> User:
    user = user_service.find_user_by_screen_name(screen_name)

    if not user:
        raise click.BadParameter('Unknown user screen name "{}".'
                                 .format(screen_name))

    return user
