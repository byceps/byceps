# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..orga.models import OrgaTeam
from ..party.models import Party

from .authorization import OrgaBirthdayPermission, OrgaTeamPermission
from .models import collect_next_orga_birthdays


blueprint = create_blueprint('orga_admin', __name__)


permission_registry.register_enum(OrgaBirthdayPermission)
permission_registry.register_enum(OrgaTeamPermission)


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
    """List orga teams for that party."""
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
    birthdays = list(collect_next_orga_birthdays())
    return {'birthdays': birthdays}
