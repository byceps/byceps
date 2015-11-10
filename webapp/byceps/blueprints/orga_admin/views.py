# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from flask import abort, request, url_for

from ...database import db
from ...util.export import serialize_to_csv
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location, textified

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..orga.models import Membership, OrgaFlag, OrgaTeam
from ..party.models import Party
from ..user.models import User

from .authorization import OrgaBirthdayPermission, OrgaDetailPermission, \
    OrgaTeamPermission
from .forms import MembershipCreateForm, MembershipUpdateForm, \
    OrgaFlagCreateForm, OrgaTeamCreateForm
from . import service
from .service import collect_orgas_with_next_birthdays, \
    get_organizers_for_brand, get_teams_for_party, \
    get_unassigned_orgas_for_party


blueprint = create_blueprint('orga_admin', __name__)


permission_registry.register_enum(OrgaBirthdayPermission)
permission_registry.register_enum(OrgaDetailPermission)
permission_registry.register_enum(OrgaTeamPermission)


@blueprint.route('/persons')
@permission_required(OrgaDetailPermission.view)
@templated
def persons():
    """List brands to choose from."""
    brands_with_person_counts = service.get_brands_with_person_counts()

    return {
        'brands_with_person_counts': brands_with_person_counts,
    }


@blueprint.route('/persons/<brand_id>')
@permission_required(OrgaDetailPermission.view)
@templated
def persons_for_brand(brand_id):
    """List organizers for the brand with details."""
    brand = Brand.query.get_or_404(brand_id)
    orgas = get_organizers_for_brand(brand)
    return {
        'brand': brand,
        'orgas': orgas,
    }


@blueprint.route('/persons/<brand_id>/create')
@permission_required(OrgaTeamPermission.administrate_memberships)
@templated
def create_orgaflag_form(brand_id):
    """Show form to give the organizer flag to a user."""
    brand = Brand.query.get_or_404(brand_id)
    form = OrgaFlagCreateForm()
    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/persons/<brand_id>', methods=['POST'])
@permission_required(OrgaTeamPermission.administrate_memberships)
def create_orgaflag(brand_id):
    """Give the organizer flag to a user."""
    brand = Brand.query.get_or_404(brand_id)
    form = OrgaFlagCreateForm(request.form)

    user_id = form.user_id.data.strip()
    user = User.query.get_or_404(user_id)

    orga_flag = OrgaFlag(
        brand=brand,
        user=user)
    db.session.add(orga_flag)
    db.session.commit()

    flash_success('{} wurde das Orga-Flag für die Marke {} gegeben.'
                  .format(user.screen_name, brand.title))
    return redirect_to('.persons_for_brand', brand_id=brand.id)


@blueprint.route('/persons/<brand_id>/<uuid:user_id>', methods=['DELETE'])
@permission_required(OrgaTeamPermission.administrate_memberships)
@respond_no_content_with_location
def remove_orgaflag(brand_id, user_id):
    """Remove the organizer flag for a brand from a person."""
    orga_flag = OrgaFlag.query \
        .filter_by(brand_id=brand_id) \
        .filter_by(user_id=user_id) \
        .first_or_404()

    brand = orga_flag.brand
    user = orga_flag.user

    db.session.delete(orga_flag)
    db.session.commit()

    flash_success('{} wurde das Orga-Flag für die Marke {} entzogen.'
                  .format(user.screen_name, brand.title))
    return url_for('.persons_for_brand', brand_id=brand.id)


@blueprint.route('/persons/<brand_id>/export')
@permission_required(OrgaDetailPermission.view)
@textified
def export_persons(brand_id):
    """Export the list of organizers for the brand as a CSV document in
    Microsoft Excel dialect.
    """
    field_names = [
        'Benutzername',
        'Vorname',
        'Nachname',
        'Geburtstag',
        'Straße',
        'PLZ',
        'Ort',
        'Land',
        'E-Mail-Adresse',
        'Telefonnummer',
    ]

    def to_dict(user):
        date_of_birth = user.detail.date_of_birth.strftime('%d.%m.%Y') \
                        if user.detail.date_of_birth else None

        return {
            'Benutzername': user.screen_name,
            'Vorname': user.detail.first_names,
            'Nachname': user.detail.last_name,
            'Geburtstag': date_of_birth,
            'Straße': user.detail.street,
            'PLZ': user.detail.zip_code,
            'Ort': user.detail.city,
            'Land': user.detail.country,
            'E-Mail-Adresse': user.email_address,
            'Telefonnummer': user.detail.phone_number,
        }

    brand = Brand.query.get_or_404(brand_id)
    orgas = get_organizers_for_brand(brand)
    orgas.sort(key=attrgetter('screen_name'))
    rows = map(to_dict, orgas)
    return serialize_to_csv(field_names, rows)


@blueprint.route('/teams')
@permission_required(OrgaTeamPermission.list)
@templated
def teams():
    """List parties to choose from."""
    parties_with_team_counts = service.get_parties_with_team_counts()

    return {
        'parties_with_team_counts': parties_with_team_counts,
    }


@blueprint.route('/teams/<party_id>')
@permission_required(OrgaTeamPermission.list)
@templated
def teams_for_party(party_id):
    """List organizer teams for that party."""
    party = Party.query.get_or_404(party_id)

    teams = OrgaTeam.query \
        .options(db.joinedload('memberships')) \
        .filter_by(party=party) \
        .all()

    return {
        'party': party,
        'teams': teams,
    }


@blueprint.route('/teams/<party_id>/create')
@permission_required(OrgaTeamPermission.create)
@templated
def team_create_form(party_id, erroneous_form=None):
    """Show form to create an organizer team for a party."""
    party = Party.query.get_or_404(party_id)

    form = erroneous_form if erroneous_form else OrgaTeamCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/teams/<party_id>', methods=['POST'])
@permission_required(OrgaTeamPermission.create)
def team_create(party_id):
    """Create an organizer team for a party."""
    party = Party.query.get_or_404(party_id)

    form = OrgaTeamCreateForm(request.form)
    if not form.validate():
        return team_create_form(party_id, form)

    title = form.title.data.strip()

    team = OrgaTeam(party, title)
    db.session.add(team)
    db.session.commit()

    flash_success('Das Team "{}" wurde für die Party "{}" erstellt.'
                  .format(team.title, team.party.title))
    return redirect_to('.teams_for_party', party_id=party.id)


@blueprint.route('/teams/<uuid:team_id>', methods=['DELETE'])
@permission_required(OrgaTeamPermission.delete)
@respond_no_content_with_location
def team_delete(team_id):
    """Delete the team."""
    team = OrgaTeam.query.get_or_404(team_id)

    if team.memberships:
        abort(403, 'Orga team cannot be deleted as it has members.')

    party = team.party
    title = team.title

    db.session.delete(team)
    db.session.commit()

    flash_success('Das Team "{}" wurde gelöscht.'.format(title))
    return url_for('.teams_for_party', party_id=party.id)


@blueprint.route('/memberships/for_party/<party_id>/create')
@permission_required(OrgaTeamPermission.administrate_memberships)
@templated
def membership_create_form(party_id, erroneous_form=None):
    """Show form to assign an organizer to a team."""
    party = Party.query.get_or_404(party_id)

    form = erroneous_form if erroneous_form else MembershipCreateForm()
    form.set_user_choices(get_unassigned_orgas_for_party(party))
    form.set_orga_team_choices(get_teams_for_party(party))

    return {
        'form': form,
        'party': party,
    }


@blueprint.route('/memberships/for_party/<party_id>', methods=['POST'])
@permission_required(OrgaTeamPermission.administrate_memberships)
def membership_create(party_id):
    """Assign an organizer to a team."""
    party = Party.query.get_or_404(party_id)

    form = MembershipCreateForm(request.form)
    form.set_user_choices(get_unassigned_orgas_for_party(party))
    form.set_orga_team_choices(get_teams_for_party(party))

    if not form.validate():
        return membership_create_form(party_id, form)

    user = User.query.get(form.user_id.data)
    team = OrgaTeam.query.get(form.orga_team_id.data)
    duties = form.duties.data.strip()

    membership = Membership(team, user)
    if duties:
        membership.duties = duties
    db.session.add(team)
    db.session.commit()

    flash_success('{} wurde in das Team "{}" aufgenommen.'
                  .format(membership.user.screen_name,
                          membership.orga_team.title))
    return redirect_to('.teams_for_party',
                       party_id=membership.orga_team.party.id)


@blueprint.route('/memberships/<uuid:id>/update')
@permission_required(OrgaTeamPermission.administrate_memberships)
@templated
def membership_update_form(id, erroneous_form=None):
    """Show form to update a membership."""
    membership = Membership.query.get_or_404(id)

    form = erroneous_form if erroneous_form \
           else MembershipUpdateForm(obj=membership)
    form.set_orga_team_choices(get_teams_for_party(membership.orga_team.party))

    return {
        'form': form,
        'membership': membership,
    }


@blueprint.route('/memberships/<uuid:id>', methods=['POST'])
@permission_required(OrgaTeamPermission.administrate_memberships)
def membership_update(id):
    """Update a membership."""
    membership = Membership.query.get_or_404(id)

    form = MembershipUpdateForm(request.form)
    form.set_orga_team_choices(get_teams_for_party(membership.orga_team.party))

    if not form.validate():
        return membership_update_form(id, form)

    membership.orga_team = OrgaTeam.query.get(form.orga_team_id.data)
    membership.duties = form.duties.data.strip() or None
    db.session.commit()

    flash_success('Die Teammitgliedschaft von {} wurde aktualisiert.',
                  membership.user.screen_name)
    return redirect_to('.teams_for_party',
                       party_id=membership.orga_team.party.id)


@blueprint.route('/memberships/<uuid:id>', methods=['DELETE'])
@permission_required(OrgaTeamPermission.administrate_memberships)
@respond_no_content_with_location
def membership_remove(id):
    """Remove an organizer from a team."""
    membership = Membership.query.get_or_404(id)

    user = membership.user
    team = membership.orga_team

    db.session.delete(membership)
    db.session.commit()

    flash_success('{} wurde aus dem Team "{}" entfernt.'
                  .format(user.screen_name, team.title))
    return url_for('.teams_for_party', party_id=team.party.id)


@blueprint.route('/birthdays')
@permission_required(OrgaBirthdayPermission.list)
@templated
def birthdays():
    orgas = list(collect_orgas_with_next_birthdays())
    return {
        'orgas': orgas,
    }
