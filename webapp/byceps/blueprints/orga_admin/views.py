# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import csv
import io
from operator import attrgetter

from ...util.framework import create_blueprint
from ...util.templating import templated
from ...util.views import textified

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..orga.models import OrgaFlag, OrgaTeam
from ..party.models import Party

from .authorization import OrgaBirthdayPermission, OrgaDetailPermission, \
    OrgaTeamPermission
from .service import collect_orgas_with_next_birthdays, get_organizers


blueprint = create_blueprint('orga_admin', __name__)


permission_registry.register_enum(OrgaBirthdayPermission)
permission_registry.register_enum(OrgaDetailPermission)
permission_registry.register_enum(OrgaTeamPermission)


@blueprint.route('/persons')
@permission_required(OrgaDetailPermission.view)
@templated
def persons():
    """List organizers with details."""
    orgas = get_organizers()
    return {'orgas': orgas}


@blueprint.route('/persons/export')
@permission_required(OrgaDetailPermission.view)
@textified
def export_persons():
    """Export the list of organizers als CSV in Microsoft Excel dialect."""
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

    orgas = get_organizers()
    rows = map(to_dict, orgas)
    return to_csv(field_names, rows)


def to_csv(field_names, rows):
    with io.StringIO(newline='') as f:
        writer = csv.DictWriter(f, field_names, dialect=csv.excel)

        writer.writeheader()
        writer.writerows(rows)

        f.seek(0)
        yield from f


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


@blueprint.route('/birthdays')
@permission_required(OrgaBirthdayPermission.list)
@templated
def birthdays():
    orgas = list(collect_orgas_with_next_birthdays())
    return {
        'orgas': orgas,
    }
