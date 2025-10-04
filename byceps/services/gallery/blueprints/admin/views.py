"""
byceps.services.gallery.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request, url_for
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand, BrandID
from byceps.services.gallery import gallery_import_service, gallery_service
from byceps.services.gallery.models import Gallery, GalleryID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content_with_location,
)

from .forms import GalleryCreateForm, GalleryUpdateForm


blueprint = create_blueprint('gallery_admin', __name__)


# -------------------------------------------------------------------- #
# gallery


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


@blueprint.get('/galleries/<uuid:gallery_id>')
@permission_required('gallery.administrate')
@templated
def gallery_view(gallery_id):
    """List galleries for that brand."""
    gallery = _get_gallery_or_404(gallery_id)

    brand = brand_service.get_brand(gallery.brand_id)

    return {
        'gallery': gallery,
        'brand': brand,
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


@blueprint.get('/galleries/<uuid:gallery_id>/update')
@permission_required('gallery.administrate')
@templated
def gallery_update_form(gallery_id, erroneous_form=None):
    """Show form to update a gallery."""
    gallery = _get_gallery_or_404(gallery_id)

    brand = brand_service.get_brand(gallery.brand_id)

    form = erroneous_form if erroneous_form else GalleryUpdateForm(obj=gallery)

    return {
        'gallery': gallery,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/galleries/<uuid:gallery_id>')
@permission_required('gallery.administrate')
def gallery_update(gallery_id):
    """Update a gallery."""
    gallery = _get_gallery_or_404(gallery_id)

    form = GalleryUpdateForm(request.form)
    if not form.validate():
        return gallery_update_form(gallery_id, form)

    title = form.title.data.strip()
    hidden = form.hidden.data

    updated_gallery = gallery_service.update_gallery(
        gallery, gallery.slug, title, hidden
    )

    flash_success(gettext('Gallery has been updated.'))

    return redirect_to('.gallery_index_for_brand', brand_id=gallery.brand_id)


@blueprint.delete('/galleries/<uuid:gallery_id>')
@permission_required('gallery.administrate')
@respond_no_content_with_location
def gallery_delete(gallery_id):
    """Delete a gallery."""
    gallery = _get_gallery_or_404(gallery_id)
    brand_id = gallery.brand_id

    gallery_service.delete_gallery(gallery_id)

    flash_success(gettext('Gallery has been deleted.'))

    return url_for('.gallery_index_for_brand', brand_id=brand_id)


# -------------------------------------------------------------------- #
# image import


@blueprint.get('/galleries/<uuid:gallery_id>/scan_images')
@permission_required('gallery.administrate')
@templated
def scan_images(gallery_id):
    """Scan for images to import in the gallery's filesystem path."""
    gallery = _get_gallery_or_404(gallery_id)

    brand = brand_service.get_brand(gallery.brand_id)

    image_file_sets = gallery_import_service.get_image_file_sets(gallery)

    return {
        'image_file_sets': image_file_sets,
        'gallery': gallery,
        'brand': brand,
    }


@blueprint.post('/galleries/<uuid:gallery_id>/import_images')
@permission_required('gallery.administrate')
def import_images(gallery_id):
    """Import images into the gallery."""
    gallery = _get_gallery_or_404(gallery_id)

    image_file_sets = gallery_import_service.get_image_file_sets(gallery)
    gallery_import_service.import_images_in_gallery_path(
        gallery, image_file_sets
    )

    flash_success(gettext('Images have been imported.'))

    return redirect_to('.gallery_view', gallery_id=gallery.id)


# -------------------------------------------------------------------- #
# helpers


def _get_brand_or_404(brand_id: BrandID) -> Brand:
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def _get_gallery_or_404(gallery_id: GalleryID) -> Gallery:
    gallery = gallery_service.find_gallery(gallery_id)

    if gallery is None:
        abort(404)

    return gallery
