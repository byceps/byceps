"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.brand.models import Brand
from byceps.services.gallery import gallery_service
from byceps.services.gallery.models import Gallery, GalleryID


@pytest.fixture(scope='module')
def gallery(admin_app, brand: Brand) -> Gallery:
    """Create a test gallery."""
    return gallery_service.create_gallery(
        brand.id,
        'test-gallery',
        'Test Gallery',
        False,
    )


def test_delete_gallery(admin_app, brand: Brand, gallery: Gallery) -> None:
    """Test that deleting a gallery removes it and its associations."""
    gallery_id: GalleryID = gallery.id

    # Verify that gallery exists.
    gallery_before = gallery_service.find_gallery(gallery_id)
    assert gallery_before is not None
    assert gallery_before.id == gallery_id

    # Delete gallery.
    gallery_service.delete_gallery(gallery_id)

    # Verify that gallery is deleted.
    gallery_after = gallery_service.find_gallery(gallery_id)
    assert gallery_after is None


def test_delete_gallery_with_images(admin_app, brand: Brand) -> None:
    """Test that deleting a gallery also deletes its images."""
    # Create gallery.
    gallery: Gallery = gallery_service.create_gallery(
        brand.id,
        'gallery-with-images',
        'Gallery With Images',
        False,
    )
    gallery_id: GalleryID = gallery.id

    # Add images to gallery.
    image1 = gallery_service.create_image(
        gallery,
        'image001.jpg',
        'image001_preview.jpg',
    )
    _ = gallery_service.create_image(
        gallery,
        'image002.jpg',
        'image002_preview.jpg',
    )

    # Set title image.
    gallery_service.set_gallery_title_image(gallery_id, image1.id)

    # Verify gallery and images exist.
    gallery_before = gallery_service.find_gallery(gallery_id)
    assert gallery_before is not None
    assert gallery_before.title_image is not None
    assert gallery_before.title_image.id == image1.id

    # Delete gallery.
    gallery_service.delete_gallery(gallery_id)

    # Verify that gallery is deleted.
    gallery_after = gallery_service.find_gallery(gallery_id)
    assert gallery_after is None
