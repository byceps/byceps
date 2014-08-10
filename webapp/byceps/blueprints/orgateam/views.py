# -*- coding: utf-8 -*-

"""
byceps.blueprints.orgateam.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint

from ..authorization.registry import permission_registry

from .authorization import OrgaTeamPermission


blueprint = create_blueprint('orgateam', __name__)


permission_registry.register_enum('orga_team', OrgaTeamPermission)
