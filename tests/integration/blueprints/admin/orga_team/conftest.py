"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask import Flask
import pytest

from byceps.services.orga_team import orga_team_service
from byceps.services.orga_team.transfer.models import OrgaTeam
from byceps.services.party.transfer.models import PartyID
from byceps.services.user.transfer.models import User

from tests.helpers import generate_token, log_in_user


@pytest.fixture(scope='package')
def orga_team_admin(make_admin) -> User:
    permission_ids = {
        'admin.access',
        'orga_team.administrate_memberships',
        'orga_team.create',
        'orga_team.delete',
        'orga_team.view',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def orga_team_admin_client(
    make_client, admin_app: Flask, orga_team_admin: User
):
    return make_client(admin_app, user_id=orga_team_admin.id)


@pytest.fixture
def make_team(admin_app: Flask):
    team_ids = []

    def _wrapper(party_id: PartyID, title: Optional[str] = None) -> OrgaTeam:
        if title is None:
            title = generate_token()

        team = orga_team_service.create_team(party_id, title)
        team_ids.append(team.id)
        return team

    yield _wrapper

    for team_id in team_ids:
        orga_team_service.delete_team(team_id)
