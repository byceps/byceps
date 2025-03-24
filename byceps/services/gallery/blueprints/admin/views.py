"""
byceps.services.gallery.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.gallery import gallery_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to

from .forms import GalleryCreateForm


blueprint = create_blueprint('gallery_admin', __name__)


@blueprint.get('/brands/<brand_id>')
@permission_required('gallery.administrate')
@templated
def gallery_index_for_brand(brand_id):
    """List galleries for that brand."""
    brand = _get_brand_or_404(brand_id)

    galleries = gallery_service.get_galleries_for_brand(brand.id)

    return {
        'brand': brand,
        'galleries': galleries,
    }


@blueprint.get('/for_brand/<brand_id>/galleries/create')
@permission_required('gallery.administrate')
@templated
def gallery_create_form(brand_id, erroneous_form=None):
    """Show form to create a gallery."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else GalleryCreateForm(brand.id)

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_brand/<brand_id>/galleries')
@permission_required('gallery.administrate')
def gallery_create(brand_id):
    """Create a board."""
    brand = _get_brand_or_404(brand_id)

    form = GalleryCreateForm(brand.id, request.form)
    if not form.validate():
        return gallery_create_form(brand.id, form)

    slug = form.slug.data.strip().lower()
    title = form.title.data.strip()
    hidden = form.hidden.data

    gallery_service.create_gallery(brand.id, slug, title, hidden)

    flash_success(gettext('Gallery has been created.'))

    return redirect_to('.gallery_index_for_brand', brand_id=brand.id)


# -------------------------------------------------------------------- #
# helpers


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand
