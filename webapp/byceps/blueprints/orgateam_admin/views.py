# -*- coding: utf-8 -*-

"""
byceps.blueprints.orgateam_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..orgateam.authorization import OrgaTeamPermission
from ..orgateam.models import OrgaTeam


blueprint = create_blueprint('orgateam_admin', __name__)


@blueprint.route('/')
@permission_required(OrgaTeamPermission.list)
@templated
def index():
    """List orga teams."""
    teams = OrgaTeam.query.all()
    return {'teams': teams}
