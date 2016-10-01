# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...services.orga_team import service as orga_team_service
from ...util.framework import create_blueprint
from ...util.templating import templated


blueprint = create_blueprint('orga', __name__)


@blueprint.route('/')
@templated
def index():
    """List organizers."""
    memberships = service.get_memberships_for_party(g.party.id)

    return {
        'memberships': memberships,
    }
