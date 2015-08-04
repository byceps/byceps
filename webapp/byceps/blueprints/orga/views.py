# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from .models import get_orgas_for_current_party


blueprint = create_blueprint('orga', __name__)


@blueprint.route('/')
@templated
def index():
    """List organizers."""
    orgas = list(get_orgas_for_current_party())
    return {'orgas': orgas}
