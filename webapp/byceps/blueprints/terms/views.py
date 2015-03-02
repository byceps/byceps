# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from . import service


blueprint = create_blueprint('terms', __name__)


@blueprint.route('/')
@templated
def view_current():
    """Show the current version of this brand's terms and conditions."""
    version = service.get_current_version()
    return {'version': version}
