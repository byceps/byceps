# -*- coding: utf-8 -*-

"""
byceps.blueprints.party_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..party.models import Party


blueprint = create_blueprint('party_admin', __name__)


@blueprint.route('/')
@templated
def index():
    """List parties."""
    parties = Party.query.all()
    return {'parties': parties}
