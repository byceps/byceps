# -*- coding: utf-8 -*-

"""
bootstrap.validators
~~~~~~~~~~~~~~~~~~~~

Validators for use with Click_.

.. _Click: http://click.pocoo.org/

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from .helpers import get_brand, get_party, get_user


def validate_brand(ctx, param, brand_id):
    brand = get_brand(brand_id)
    if not brand:
        raise click.BadParameter('Unknown brand ID "{}".'.format(brand_id))

    return brand


def validate_party(ctx, param, party_id):
    party = get_party(party_id)
    if not party:
        raise click.BadParameter('Unknown party ID "{}".'.format(party_id))

    return party


def validate_user_screen_name(ctx, param, screen_name):
    user = get_user(screen_name)
    if not user:
        raise click.BadParameter('Unknown user screen name "{}".'.format(screen_name))

    return user
