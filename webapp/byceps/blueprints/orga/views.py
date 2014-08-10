# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..orgateam.models import get_orgas


blueprint = create_blueprint('orga', __name__)


@blueprint.route('/')
@templated
def index():
    """List organizers."""
    orgas = list(get_orgas())
    return {'orgas': orgas}
