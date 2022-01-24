"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator

import pytest

from byceps.services.orga import service as orga_service
from byceps.services.orga_team import service as orga_team_service
from byceps.services.orga_team.transfer.models import OrgaTeam
from byceps.services.party.transfer.models import Party


@pytest.fixture(scope='module')
def team_support(party: Party) -> Iterator[OrgaTeam]:
    team = orga_team_service.create_team(party.id, 'Support')
    yield team
    orga_team_service.delete_team(team.id)


@pytest.fixture(scope='module')
def team_tournaments(party: Party) -> Iterator[OrgaTeam]:
    team = orga_team_service.create_team(party.id, 'Tournaments')
    yield team
    orga_team_service.delete_team(team.id)


def test_membership_create_form(
    orga_team_admin_client, team_tournaments: OrgaTeam
) -> None:
    team = team_tournaments
    url = f'/admin/orga_teams/teams/{team.id}/memberships/create'
    response = orga_team_admin_client.get(url)
    assert response.status_code == 200


def test_membership_create(
    orga_team_admin_client, party: Party, team_tournaments: OrgaTeam, make_user
) -> None:
    user = make_user()
    team = team_tournaments
    orga_flag = orga_service.add_orga_flag(party.brand_id, user.id, user.id)

    assert orga_team_service.count_memberships_for_party(party.id) == 0

    url = f'/admin/orga_teams/teams/{team.id}/memberships'
    form_data = {
        'user_id': str(user.id),
        'duties': 'Tricky Towers',
    }
    response = orga_team_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    memberships = orga_team_service.get_memberships_for_party(party.id)
    assert len(memberships) == 1

    membership = list(memberships)[0]
    assert membership.orga_team_id == team.id
    assert membership.user_id == user.id
    assert membership.duties == 'Tricky Towers'

    # Clean up.
    orga_team_service.delete_membership(membership.id)
    orga_service.remove_orga_flag(party.brand_id, user.id, user.id)


def test_membership_update_form(
    orga_team_admin_client, party: Party, team_tournaments: OrgaTeam, make_user
) -> None:
    user = make_user()
    team = team_tournaments
    membership = orga_team_service.create_membership(team.id, user.id, 'PUBG')

    url = f'/admin/orga_teams/memberships/{membership.id}/update'
    response = orga_team_admin_client.get(url)
    assert response.status_code == 200

    # Clean up.
    orga_team_service.delete_membership(membership.id)


def test_membership_update(
    orga_team_admin_client,
    party: Party,
    team_support: OrgaTeam,
    team_tournaments: OrgaTeam,
    make_user,
) -> None:
    user = make_user()
    team1 = team_support
    team2 = team_tournaments
    membership_before = orga_team_service.create_membership(
        team1.id, user.id, 'all'
    )

    assert membership_before.orga_team_id == team1.id
    assert membership_before.duties == 'all'

    url = f'/admin/orga_teams/memberships/{membership_before.id}'
    form_data = {
        'orga_team_id': str(team2.id),
        'duties': 'Overwatch',
    }
    response = orga_team_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    membership_after = orga_team_service.find_membership(membership_before.id)
    assert membership_after is not None
    assert membership_after.orga_team_id == team2.id
    assert membership_after.duties == 'Overwatch'

    # Clean up.
    orga_team_service.delete_membership(membership_before.id)


def test_membership_remove(
    orga_team_admin_client, party: Party, team_tournaments: OrgaTeam, make_user
) -> None:
    user = make_user()
    team = team_tournaments
    membership = orga_team_service.create_membership(team.id, user.id, 'CS:GO')

    url = f'/admin/orga_teams/memberships/{membership.id}'
    response = orga_team_admin_client.delete(url)
    assert response.status_code == 204

    # Clean up.
    orga_team_service.delete_membership(membership.id)
