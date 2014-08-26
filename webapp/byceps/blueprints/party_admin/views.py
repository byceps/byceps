# -*- coding: utf-8 -*-

"""
byceps.blueprints.party_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party.models import Party

from .authorization import PartyPermission


blueprint = create_blueprint('party_admin', __name__)


permission_registry.register_enum(PartyPermission)


@blueprint.route('/')
@permission_required(PartyPermission.list)
@templated
def index():
    """List parties."""
    parties = Party.query.all()
    return {'parties': parties}
