"""
byceps.services.demo_data.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g
from flask_babel import gettext

from byceps.services.demo_data import demo_data_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to


blueprint = create_blueprint('demo_data_admin', __name__)


@blueprint.get('')
@permission_required('board.create')
@permission_required('board_category.create')
@permission_required('brand.create')
@permission_required('page.create')
@permission_required('party.create')
@permission_required('shop.create')
@permission_required('shop_product.administrate')
@permission_required('site.create')
@permission_required('site_navigation.administrate')
@permission_required('ticketing.administrate')
@templated
def index():
    """Show control to add data for demonstration purposes."""
    demo_data_exists = demo_data_service.does_demo_data_exist()

    return {
        'demo_data_exists': demo_data_exists,
    }


@blueprint.post('/')
@permission_required('board.create')
@permission_required('board_category.create')
@permission_required('brand.create')
@permission_required('page.create')
@permission_required('party.create')
@permission_required('shop.create')
@permission_required('shop_product.administrate')
@permission_required('site.create')
@permission_required('site_navigation.administrate')
@permission_required('ticketing.administrate')
def create():
    """Add data for demonstration purposes."""
    if demo_data_service.does_demo_data_exist():
        flash_notice(gettext('Demonstration data already exists.'))
        return redirect_to('.index')

    creator = g.user
    demo_data_service.create_demo_data(creator)

    flash_success(gettext('Demonstration data has been created.'))

    return redirect_to('.index')
