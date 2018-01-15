"""
byceps.blueprints.core_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...services.brand import service as brand_service
from ...util.framework.blueprint import create_blueprint

from ..authorization.registry import permission_registry

from .authorization import AdminPermission


blueprint = create_blueprint('core_admin', __name__)


permission_registry.register_enum(AdminPermission)


@blueprint.app_context_processor
def inject_brands():
    brands = brand_service.get_brands()

    return {
        'all_brands': brands,
    }
