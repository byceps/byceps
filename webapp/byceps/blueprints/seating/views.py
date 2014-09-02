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


@blueprint.route('/areas/<slug>')
@templated
def view_area(slug):
    """View area."""
    area = Area.query.for_current_party().filter_by(slug=slug).first_or_404()
    return {'area': area}
