"""
byceps.services.gallery.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from byceps.services.gallery import gallery_service
from byceps.services.site.blueprints.site.navigation import (
    subnavigation_for_view,
)
from byceps.util.authz import has_current_user_permission
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('gallery', __name__)


@blueprint.get('/')
@templated
@subnavigation_for_view('gallery')
def index():
    """List all galleries for this brand."""
    galleries = gallery_service.get_galleries_for_brand(g.brand_id)

    if not _may_current_user_view_hidden():
        galleries = [g for g in galleries if not g.hidden]

    return {'galleries': galleries}


@blueprint.get('/<slug>')
@templated
@subnavigation_for_view('gallery')
def view(slug):
    """Show gallery for this brand with that slug."""
    gallery = gallery_service.find_gallery_by_slug_with_images(g.brand_id, slug)

    if not gallery:
        abort(404)

    if gallery.hidden and not _may_current_user_view_hidden():
        abort(404)

    return {'gallery': gallery}


def _may_current_user_view_hidden() -> bool:
    return has_current_user_permission('gallery.view_hidden')
