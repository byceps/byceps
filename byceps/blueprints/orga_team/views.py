# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_team.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...services.orga_team import service as orga_team_service
from ...util.framework.blueprint import create_blueprint
from ...util.templating import templated


blueprint = create_blueprint('orga_team', __name__)


@blueprint.route('/')
@templated
def index():
    """List all organizers for the current party."""
    memberships = orga_team_service.get_memberships_for_party(g.party.id)

    return {
        'memberships': memberships,
    }
