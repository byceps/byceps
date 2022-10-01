"""
byceps.blueprints.admin.orga_team.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from ....services.orga_team import service as orga_team_service
from ....services.party import service as party_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to, respond_no_content

from .forms import (
    MembershipCreateForm,
    MembershipUpdateForm,
    OrgaTeamCreateForm,
    OrgaTeamsCopyForm,
)


blueprint = create_blueprint('orga_team_admin', __name__)


# -------------------------------------------------------------------- #
# teams


@blueprint.get('/teams/<party_id>')
@permission_required('orga_team.view')
@templated
def teams_for_party(party_id):
    """List organizer teams for that party."""
    party = _get_party_or_404(party_id)

    teams_and_members = orga_team_service.get_teams_and_members_for_party(
        party.id
    )

    def sort_members(members):
        return sorted(
            members,
            key=lambda m: user_service.get_sort_key_for_screen_name(m.user),
        )

    teams_and_members = sorted(teams_and_members, key=lambda tam: tam[0].title)
    teams_and_members = [
        (teams, sort_members(members)) for teams, members in teams_and_members
    ]

    return {
        'party': party,
        'teams_and_members': teams_and_members,
    }


@blueprint.get('/teams/<party_id>/create')
@permission_required('orga_team.create')
@templated
def team_create_form(party_id, erroneous_form=None):
    """Show form to create an organizer team for a party."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else OrgaTeamCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/teams/<party_id>')
@permission_required('orga_team.create')
def team_create(party_id):
    """Create an organizer team for a party."""
    party = _get_party_or_404(party_id)

    form = OrgaTeamCreateForm(request.form)
    if not form.validate():
        return team_create_form(party.id, form)

    title = form.title.data.strip()

    team = orga_team_service.create_team(party.id, title)

    flash_success(
        gettext(
            'Team "%(team_title)s" for party "%(party_title)s" has been created.',
            team_title=team.title,
            party_title=party.title,
        )
    )
    return redirect_to('.teams_for_party', party_id=party.id)


@blueprint.delete('/teams/<uuid:team_id>')
@permission_required('orga_team.delete')
@respond_no_content
def team_delete(team_id):
    """Delete the team."""
    team = _get_team_or_404(team_id)

    if orga_team_service.has_team_memberships(team.id):
        flash_error(
            gettext(
                'Team "%(team_title)s" cannot be deleted because it has members.',
                team_title=team.title,
            )
        )
        return

    title = team.title

    orga_team_service.delete_team(team.id)

    flash_success(gettext('Team "%(title)s" has been deleted.', title=title))


@blueprint.get('/teams/<target_party_id>/copy')
@permission_required('orga_team.create')
@templated
def teams_copy_form(target_party_id, erroneous_form=None):
    """Show form to copy all organizer teams from another party."""
    target_party = _get_party_or_404(target_party_id)

    team_count = orga_team_service.count_teams_for_party(target_party.id)
    if team_count:
        flash_error(
            gettext(
                'This party already has teams. No additional teams can be copied to it.'
            )
        )
        return redirect_to('.teams_for_party', party_id=target_party.id)

    parties = party_service.get_parties_for_brand(target_party.brand_id)

    # Do not offer to copy teams from target party.
    parties = [p for p in parties if p.id != target_party.id]

    party_ids = {party.id for party in parties}
    team_count_per_party = orga_team_service.count_teams_for_parties(party_ids)

    # Exclude parties without orga teams.
    parties = [p for p in parties if team_count_per_party.get(p.id, 0)]

    if not parties:
        flash_error(
            gettext('No other parties exist from which teams could be copied.')
        )
        return redirect_to('.teams_for_party', party_id=target_party.id)

    parties.sort(key=lambda p: p.starts_at, reverse=True)

    form = erroneous_form if erroneous_form else OrgaTeamsCopyForm()
    form.set_party_choices(parties, team_count_per_party)

    return {
        'party': target_party,
        'form': form,
    }


@blueprint.post('/teams/<target_party_id>/copy')
@permission_required('orga_team.create')
def teams_copy(target_party_id):
    """Copy all organizer teams from another party."""
    target_party = _get_party_or_404(target_party_id)

    target_team_count = orga_team_service.count_teams_for_party(target_party.id)
    if target_team_count:
        flash_error(
            gettext(
                'This party already has teams. No additional teams can be copied to it.'
            )
        )
        return redirect_to('.teams_for_party', party_id=target_party.id)

    parties = party_service.get_parties_for_brand(target_party.brand_id)

    form = OrgaTeamsCopyForm(request.form)
    form.set_party_choices(parties)
    if not form.validate():
        return teams_copy_form(target_party.id, form)

    source_party = party_service.get_party(form.party_id.data)

    copied_teams_count = orga_team_service.copy_teams_and_memberships(
        source_party.id, target_party.id
    )

    flash_success(
        gettext(
            '%(copied_teams_count)s team(s) has/have been copied from party '
            '"%(source_party_title)s" to party "%(target_party_title)s".',
            copied_teams_count=copied_teams_count,
            source_party_title=source_party.title,
            target_party_title=target_party.title,
        )
    )

    return redirect_to('.teams_for_party', party_id=target_party.id)


# -------------------------------------------------------------------- #
# memberships


@blueprint.get('/teams/<uuid:team_id>/memberships/create')
@permission_required('orga_team.administrate_memberships')
@templated
def membership_create_form(team_id, erroneous_form=None):
    """Show form to assign an organizer to that team."""
    team = _get_team_or_404(team_id)

    party = party_service.get_party(team.party_id)

    unassigned_orgas = orga_team_service.get_unassigned_orgas_for_team(team)

    if not unassigned_orgas:
        return {
            'team': team,
            'party': party,
            'unassigned_orgas_available': False,
        }

    unassigned_orgas = sorted(
        unassigned_orgas, key=user_service.get_sort_key_for_screen_name
    )

    form = erroneous_form if erroneous_form else MembershipCreateForm()
    form.set_user_choices(unassigned_orgas)

    return {
        'form': form,
        'team': team,
        'party': party,
        'unassigned_orgas_available': True,
    }


@blueprint.post('/teams/<uuid:team_id>/memberships')
@permission_required('orga_team.administrate_memberships')
def membership_create(team_id):
    """Assign an organizer to that team."""
    team = _get_team_or_404(team_id)

    unassigned_orgas = orga_team_service.get_unassigned_orgas_for_team(team)

    form = MembershipCreateForm(request.form)
    form.set_user_choices(unassigned_orgas)

    if not form.validate():
        return membership_create_form(team.id, form)

    user = user_service.get_user(form.user_id.data)
    duties = form.duties.data.strip()

    orga_team_service.create_membership(team.id, user.id, duties)

    flash_success(
        gettext(
            '%(screen_name)s has been added to team "%(team_title)s".',
            screen_name=user.screen_name,
            team_title=team.title,
        )
    )
    return redirect_to('.teams_for_party', party_id=team.party_id)


@blueprint.get('/memberships/<uuid:membership_id>/update')
@permission_required('orga_team.administrate_memberships')
@templated
def membership_update_form(membership_id, erroneous_form=None):
    """Show form to update a membership."""
    membership = _get_membership_or_404(membership_id)

    user = user_service.get_user(membership.user_id)
    team = orga_team_service.find_team(membership.orga_team_id)
    party = party_service.get_party(team.party_id)

    teams = orga_team_service.get_teams_for_party(team.party_id)

    form = (
        erroneous_form
        if erroneous_form
        else MembershipUpdateForm(obj=membership)
    )
    form.set_orga_team_choices(teams)

    return {
        'form': form,
        'membership': membership,
        'user': user,
        'team': team,
        'party': party,
    }


@blueprint.post('/memberships/<uuid:membership_id>')
@permission_required('orga_team.administrate_memberships')
def membership_update(membership_id):
    """Update a membership."""
    membership = _get_membership_or_404(membership_id)

    user = user_service.get_user(membership.user_id)
    team = orga_team_service.find_team(membership.orga_team_id)

    teams = orga_team_service.get_teams_for_party(team.party_id)

    form = MembershipUpdateForm(request.form)
    form.set_orga_team_choices(teams)

    if not form.validate():
        return membership_update_form(membership.id, form)

    team_id = form.orga_team_id.data
    team = orga_team_service.find_team(team_id)
    duties = form.duties.data.strip() or None

    orga_team_service.update_membership(membership.id, team.id, duties)

    flash_success(
        gettext(
            'Membership of %(screen_name)s has been updated.',
            screen_name=user.screen_name,
        )
    )
    return redirect_to('.teams_for_party', party_id=team.party_id)


@blueprint.delete('/memberships/<uuid:membership_id>')
@permission_required('orga_team.administrate_memberships')
@respond_no_content
def membership_remove(membership_id):
    """Remove an organizer from a team."""
    membership = _get_membership_or_404(membership_id)

    user = user_service.get_user(membership.user_id)
    team = orga_team_service.find_team(membership.orga_team_id)

    orga_team_service.delete_membership(membership.id)

    flash_success(
        gettext(
            '%(screen_name)s has been removed from team "%(team_title)s".',
            screen_name=user.screen_name,
            team_title=team.title,
        )
    )


# -------------------------------------------------------------------- #
# helpers


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
