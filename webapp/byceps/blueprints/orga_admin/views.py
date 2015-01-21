# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from operator import attrgetter

from flask import url_for

from ...database import db
from ...util.export import serialize_to_csv
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import respond_no_content_with_location, textified

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..orga.models import Membership, OrgaTeam
from ..party.models import Party

from .authorization import OrgaBirthdayPermission, OrgaDetailPermission, \
    OrgaTeamPermission
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
    """List organizers with details."""
    brand = Brand.query.get_or_404(brand_id)
    orgas = get_organizers_for_brand(brand)
    return {
        'brand': brand,
        'orgas': orgas,
    }


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
    teams = OrgaTeam.query.all()
    return {
        'teams': teams,
        'party': party,
    }


@blueprint.route('/memberships/<id>', methods=['DELETE'])
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
