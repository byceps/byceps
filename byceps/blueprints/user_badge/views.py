# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework import create_blueprint

from . import models  # Make `User.badges` association available.


blueprint = create_blueprint('user_badge', __name__)
