# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from .models import Area


blueprint = create_blueprint('seating', __name__)


@blueprint.route('/')
@templated
def index():
    """List areas."""
    areas = Area.query.for_current_party().all()
    return {'areas': areas}


@blueprint.route('/areas/<id>')
@templated
def view_area(id):
    """View area."""
    area = Area.query.get_or_404(id)
    return {'area': area}
