# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from operator import attrgetter

from flask import request, url_for

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
from .forms import MembershipUpdateForm, OrgaFlagCreateForm
from .service import collect_orgas_with_next_birthdays, get_organizers_for_brand


blueprint = create_blueprint('orga_admin', __name__)


permission_registry.register_enum(OrgaBirthdayPermission)
permission_registry.register_enum(OrgaDetailPermission)
permission_registry.register_enum(OrgaTeamPermission)


@blueprint.route('/persons')
@permission_required(OrgaDetailPermission.view)
@templated
def persons():
    """List brands to choose from."""
    brands = Brand.query.all()
    return {'brands': brands}


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
    parties = Party.query.all()
    return {'parties': parties}


@blueprint.route('/teams/<party_id>')
@permission_required(OrgaTeamPermission.list)
@templated
def teams_for_party(party_id):
    """List organizer teams for that party."""
    party = Party.query.get_or_404(party_id)
    teams = OrgaTeam.query \
        .options(db.joinedload('memberships')) \
        .all()
    return {
        'teams': teams,
        'party': party,
    }


@blueprint.route('/memberships/<uuid:id>/update')
@permission_required(OrgaTeamPermission.administrate_memberships)
@templated
def membership_update_form(id):
    """Show form to update a membership."""
    membership = Membership.query.get_or_404(id)

    form = MembershipUpdateForm(obj=membership)

    return {
        'form': form,
        'membership': membership,
    }


@blueprint.route('/memberships/<uuid:id>', methods=['POST'])
@permission_required(OrgaTeamPermission.administrate_memberships)
def membership_update(id):
    """Update a membership."""
    form = MembershipUpdateForm(request.form)

    membership = Membership.query.get_or_404(id)
    membership.duties = form.duties.data.strip() or None
    db.session.commit()

    flash_success('Der Aufgabe von {} wurde aktualisiert.',
                  membership.user.screen_name)
    return redirect_to('.teams_for_party', party_id=membership.party.id)


@blueprint.route('/memberships/<uuid:id>', methods=['DELETE'])
@permission_required(OrgaTeamPermission.administrate_memberships)
@respond_no_content_with_location
def membership_remove(id):
    """Remove an organizer from a team."""
    membership = Membership.query.get_or_404(id)

    user = membership.user
    party = membership.party
    team = membership.orga_team

    db.session.delete(membership)
    db.session.commit()

    flash_success(
        '{} wurde für die Veranstaltung "{}" aus dem Team "{}" entfernt.' \
            .format(user.screen_name, party.title, team.title))
    return url_for('.teams_for_party', party_id=party.id)


@blueprint.route('/birthdays')
@permission_required(OrgaBirthdayPermission.list)
@templated
def birthdays():
    orgas = list(collect_orgas_with_next_birthdays())
    return {
        'orgas': orgas,
    }
