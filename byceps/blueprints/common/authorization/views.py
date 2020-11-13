"""
byceps.blueprints.common.authorization.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....util.framework.blueprint import create_blueprint

from .registry import permission_registry


blueprint = create_blueprint('authorization', __name__)


@blueprint.app_context_processor
def add_permission_enums_to_template_context():
    return {e.__name__: e for e in permission_registry.get_enums()}
