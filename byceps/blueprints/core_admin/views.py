# -*- coding: utf-8 -*-

"""
byceps.blueprints.core_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework import create_blueprint

from ..brand.models import Brand


blueprint = create_blueprint('core_admin', __name__)


@blueprint.app_context_processor
def inject_brands():
    return {
        'all_brands': Brand.query.all(),
    }
