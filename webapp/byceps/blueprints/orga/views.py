# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...util.framework import create_blueprint
from ...util.templating import templated

from . import service


blueprint = create_blueprint('orga', __name__)


@blueprint.route('/')
@templated
def index():
    """List organizers."""
    memberships = service.get_team_memberships_for_party(g.party)
    return {'memberships': memberships}
