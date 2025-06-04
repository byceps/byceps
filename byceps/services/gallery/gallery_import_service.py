"""
byceps.services.gallery.gallery_import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from flask import current_app

from . import gallery_service
from .models import Gallery


@dataclass(frozen=True, order=True)
class ImageFileSet:
    full_filename: str
    preview_filename: str


def get_image_file_sets(
    gallery: Gallery,
    *,
    data_path: Path | None = None,
    image_suffix: str = 'jpg',
    preview_marker: str = '_preview',
) -> list[ImageFileSet]:
    """Get sets of image filenames found in the gallery's filesystem path."""
    gallery_path = _get_gallery_filesystem_path(data_path, gallery)

    image_file_sets = list(
        _get_file_sets(gallery_path, image_suffix, preview_marker)
    )
    image_file_sets.sort()

    return image_file_sets


def import_images_in_gallery_path(
    gallery: Gallery,
    image_file_sets: list[ImageFileSet],
) -> None:
    """Import all matching files in the gallery's path as images."""
    for image_file_set in sorted(image_file_sets):
        gallery_service.create_image(
            gallery,
            image_file_set.full_filename,
            image_file_set.preview_filename,
        )


def _get_gallery_filesystem_path(
    data_path: Path | None, gallery: Gallery
) -> Path:
    if data_path is None:
        data_path = current_app.byceps_config.data_path

    return data_path / 'brands' / gallery.brand_id / 'galleries' / gallery.slug


def _get_file_sets(
    gallery_path: Path, suffix: str, preview_marker: str
) -> Iterator[ImageFileSet]:
    image_filenames = _get_image_filenames(gallery_path, suffix)

    full_image_filenames = _select_full_image_filenames(
        image_filenames, preview_marker
    )

    for full_image_filename in full_image_filenames:
        yield _create_image_file_set(full_image_filename, preview_marker)


def _get_image_filenames(gallery_path: Path, suffix: str) -> Iterator[Path]:
    for image_path in gallery_path.glob(f'*.{suffix}'):
        yield Path(image_path.name)


def _select_full_image_filenames(
    image_filenames: Iterable[Path], preview_marker: str
) -> Iterator[Path]:
    def is_full_image_file(filename: Path) -> bool:
        return not filename.stem.endswith(preview_marker)

    return filter(is_full_image_file, image_filenames)


def _create_image_file_set(
    image_filename: Path, preview_marker: str
) -> ImageFileSet:
    full_filename = image_filename.name
    preview_filename = image_filename.with_stem(
        image_filename.stem + preview_marker
    ).name

    return ImageFileSet(
        full_filename=full_filename, preview_filename=preview_filename
    )
