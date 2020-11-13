#!/usr/bin/env python

"""Find user login events for an IP address.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Dict, List

import click

from byceps.services.user.models.event import UserEvent
from byceps.services.user import service as user_service
from byceps.services.user.transfer.models import User
from byceps.typing import PartyID, UserID
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.argument('ip_address')
def execute(ip_address: str):
    events = find_events(ip_address)
    users_by_id = get_users_by_id(events)

    for event in events:
        user = users_by_id[event.user_id]
        click.echo(f'{event.occurred_at}\t{ip_address}\t{user.screen_name}')


def find_events(ip_address: str) -> List[UserEvent]:
    return UserEvent.query \
        .filter_by(event_type='user-logged-in') \
        .filter(UserEvent.data['ip_address'].astext == ip_address) \
        .order_by(UserEvent.occurred_at) \
        .all()


def get_users_by_id(events: List[UserEvent]) -> Dict[UserID, User]:
    user_ids = {event.user_id for event in events}
    users = user_service.find_users(user_ids)
    return {user.id: user for user in users}


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
