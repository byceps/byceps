# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint

from .models import Permission


blueprint = create_blueprint('authorization', __name__)
