"""
byceps.blueprints.admin.orga_team.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.orga_team import service as orga_team_service
from ....services.party import service as party_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to, respond_no_content

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import OrgaTeamPermission
from .forms import (
    MembershipCreateForm,
    MembershipUpdateForm,
    OrgaTeamCreateForm,
)


blueprint = create_blueprint('orga_team_admin', __name__)


permission_registry.register_enum(OrgaTeamPermission)


@blueprint.route('/teams/<party_id>')
@permission_required(OrgaTeamPermission.view)
@templated
def teams_for_party(party_id):
    """List organizer teams for that party."""
    party = _get_party_or_404(party_id)

    teams = orga_team_service.get_teams_for_party_with_memberships(party.id)

    return {
        'party': party,
        'teams': teams,
    }


@blueprint.route('/teams/<party_id>/create')
@permission_required(OrgaTeamPermission.create)
@templated
def team_create_form(party_id, erroneous_form=None):
    """Show form to create an organizer team for a party."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else OrgaTeamCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/teams/<party_id>', methods=['POST'])
@permission_required(OrgaTeamPermission.create)
def team_create(party_id):
    """Create an organizer team for a party."""
    party = _get_party_or_404(party_id)

    form = OrgaTeamCreateForm(request.form)
    if not form.validate():
        return team_create_form(party.id, form)

    title = form.title.data.strip()

    team = orga_team_service.create_team(party.id, title)

    flash_success(
        f'Das Team "{team.title}" wurde '
        f'für die Party "{team.party.title}" erstellt.'
    )
    return redirect_to('.teams_for_party', party_id=party.id)


@blueprint.route('/teams/<uuid:team_id>', methods=['DELETE'])
@permission_required(OrgaTeamPermission.delete)
@respond_no_content
def team_delete(team_id):
    """Delete the team."""
    team = _get_team_or_404(team_id)

    if team.memberships:
        abort(403, 'Orga team cannot be deleted as it has members.')

    title = team.title

    orga_team_service.delete_team(team)

    flash_success(f'Das Team "{title}" wurde gelöscht.')


@blueprint.route('/teams/<uuid:team_id>/memberships/create')
@permission_required(OrgaTeamPermission.administrate_memberships)
@templated
def membership_create_form(team_id, erroneous_form=None):
    """Show form to assign an organizer to that team."""
    team = _get_team_or_404(team_id)

    unassigned_orgas = orga_team_service.get_unassigned_orgas_for_party(
        team.party_id
    )

    if not unassigned_orgas:
        return {
            'team': team,
            'unassigned_orgas_available': False,
        }

    form = erroneous_form if erroneous_form else MembershipCreateForm()
    form.set_user_choices(unassigned_orgas)

    return {
        'form': form,
        'team': team,
        'unassigned_orgas_available': True,
    }


@blueprint.route('/teams/<uuid:team_id>/memberships', methods=['POST'])
@permission_required(OrgaTeamPermission.administrate_memberships)
def membership_create(team_id):
    """Assign an organizer to that team."""
    team = _get_team_or_404(team_id)

    unassigned_orgas = orga_team_service.get_unassigned_orgas_for_party(
        team.party_id
    )

    form = MembershipCreateForm(request.form)
    form.set_user_choices(unassigned_orgas)

    if not form.validate():
        return membership_create_form(team.id, form)

    user = user_service.find_user(form.user_id.data)
    duties = form.duties.data.strip()

    membership = orga_team_service.create_membership(team.id, user.id, duties)

    flash_success(
        f'{membership.user.screen_name} wurde '
        f'in das Team "{membership.orga_team.title}" aufgenommen.'
    )
    return redirect_to(
        '.teams_for_party', party_id=membership.orga_team.party_id
    )


@blueprint.route('/memberships/<uuid:membership_id>/update')
@permission_required(OrgaTeamPermission.administrate_memberships)
@templated
def membership_update_form(membership_id, erroneous_form=None):
    """Show form to update a membership."""
    membership = _get_membership_or_404(membership_id)

    teams = orga_team_service.get_teams_for_party(membership.orga_team.party_id)

    form = erroneous_form if erroneous_form \
           else MembershipUpdateForm(obj=membership)
    form.set_orga_team_choices(teams)

    return {
        'form': form,
        'membership': membership,
    }


@blueprint.route('/memberships/<uuid:membership_id>', methods=['POST'])
@permission_required(OrgaTeamPermission.administrate_memberships)
def membership_update(membership_id):
    """Update a membership."""
    membership = _get_membership_or_404(membership_id)

    teams = orga_team_service.get_teams_for_party(membership.orga_team.party_id)

    form = MembershipUpdateForm(request.form)
    form.set_orga_team_choices(teams)

    if not form.validate():
        return membership_update_form(membership.id, form)

    team_id = form.orga_team_id.data
    team = orga_team_service.find_team(team_id)
    duties = form.duties.data.strip() or None

    orga_team_service.update_membership(membership, team, duties)

    flash_success(
        f'Die Teammitgliedschaft von {membership.user.screen_name} '
        'wurde aktualisiert.'
    )
    return redirect_to(
        '.teams_for_party', party_id=membership.orga_team.party_id
    )


@blueprint.route('/memberships/<uuid:membership_id>', methods=['DELETE'])
@permission_required(OrgaTeamPermission.administrate_memberships)
@respond_no_content
def membership_remove(membership_id):
    """Remove an organizer from a team."""
    membership = _get_membership_or_404(membership_id)

    user = membership.user
    team = membership.orga_team

    orga_team_service.delete_membership(membership)

    flash_success(
        f'{user.screen_name} wurde aus dem Team "{team.title}" entfernt.'
    )


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_team_or_404(team_id):
    team = orga_team_service.find_team(team_id)

    if team is None:
        abort(404)

    return team


def _get_membership_or_404(membership_id):
    membership = orga_team_service.find_membership(membership_id)

    if membership is None:
        abort(404)

    return membership
