# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import current_app, g

from ...util.framework import create_blueprint
from ...util.templating import templated

from .models import Party


blueprint = create_blueprint('party', __name__)


@blueprint.before_app_request
def before_request():
    g.party = Party.query.get(current_app.party_id)
    if g.party is None:
        raise Exception('Unknown party "{}".'.format(party_id))


@blueprint.route('/info')
@templated
def info():
    """Show information about the current party."""
