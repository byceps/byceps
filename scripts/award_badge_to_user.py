#!/usr/bin/env python

"""Award a badge to a user.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.database import db
from byceps.services.user_badge.models.badge import Badge, BadgeID
from byceps.services.user_badge import service as badge_service
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.validators import validate_user_screen_name
from bootstrap.util import app_context


@click.command()
@click.argument('badge_slug')
@click.argument('user', callback=validate_user_screen_name)
def execute(badge_slug, user):
    badge_id = find_badge_id_for_badge_slug(badge_slug)

    click.echo('Awarding badge "{}" to user "{}" ... '
        .format(badge_slug, user.screen_name), nl=False)

    badge_service.award_badge_to_user(badge_id, user.id)

    click.secho('done.', fg='green')


def find_badge_id_for_badge_slug(slug: str) -> BadgeID:
    """Finde the badge with that slug and return its ID, or raise an
    error if not found.
    """
    badge_id = db.session \
        .query(Badge.id) \
        .filter_by(slug=slug) \
        .scalar()

    if badge_id is None:
        raise click.BadParameter('Unknown badge slug "{}".'.format(slug))

    return badge_id


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
