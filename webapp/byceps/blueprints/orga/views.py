# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from .service import get_team_memberships_for_current_party


blueprint = create_blueprint('orga', __name__)


@blueprint.route('/')
@templated
def index():
    """List organizers."""
    memberships = get_team_memberships_for_current_party()
    return {'memberships': memberships}
