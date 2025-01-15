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
class ImageFilenameSet:
    full: str
    preview: str


def import_images_in_gallery_path(gallery: Gallery) -> None:
    """Import all matching files in the gallery's path as images."""
    gallery_path = _get_gallery_filesystem_path(gallery)
    image_suffix = 'jpg'
    preview_marker = '_preview'

    image_filename_sets = _get_filename_sets(
        gallery_path, image_suffix, preview_marker
    )

    for image_filename_set in sorted(image_filename_sets):
        gallery_service.create_image(
            gallery, image_filename_set.full, image_filename_set.preview
        )


def _get_gallery_filesystem_path(gallery: Gallery) -> Path:
    data_path = current_app.config['PATH_DATA']
    return data_path / 'brands' / gallery.brand_id / 'galleries' / gallery.slug


def _get_filename_sets(
    gallery_path: Path, suffix: str, preview_marker: str
) -> Iterator[ImageFilenameSet]:
    image_filenames = _get_image_filenames(gallery_path, suffix)

    full_image_filenames = _select_full_image_filenames(
        image_filenames, preview_marker
    )

    for full_image_filename in full_image_filenames:
        yield _create_image_filename_set(full_image_filename, preview_marker)


def _get_image_filenames(gallery_path: Path, suffix: str) -> Iterator[Path]:
    image_paths = gallery_path.glob(f'*.{suffix}')

    def to_filename_path(image_path: Path) -> Path:
        return Path(image_path.name)

    return map(to_filename_path, image_paths)


def _select_full_image_filenames(
    image_filenames: Iterable[Path], preview_marker: str
) -> Iterator[Path]:
    def is_full_image_file(filename: Path) -> bool:
        return not filename.stem.endswith(preview_marker)

    return filter(is_full_image_file, image_filenames)


def _create_image_filename_set(
    image_filename: Path, preview_marker: str
) -> ImageFilenameSet:
    full_filename = image_filename.name
    preview_filename = image_filename.with_stem(
        image_filename.stem + preview_marker
    ).name

    return ImageFilenameSet(full=full_filename, preview=preview_filename)
