"""
byceps.blueprints.admin.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....services.brand import service as brand_service
from ....services.party import service as party_service
from ....services.site import service as site_service
from ....util.framework.blueprint import create_blueprint

from ...common.authorization.registry import permission_registry

from .authorization import AdminPermission


blueprint = create_blueprint('core_admin', __name__)


permission_registry.register_enum(AdminPermission)


@blueprint.app_context_processor
def inject_template_variables():
    brands = brand_service.get_all_brands()

    def get_brand_for_party(party):
        return brand_service.find_brand(party.brand_id)

    return {
        'all_brands': brands,
        'get_brand_for_party': get_brand_for_party,
        'get_parties_for_brand': party_service.get_parties_for_brand,
        'get_all_sites': site_service.get_all_sites,
    }
