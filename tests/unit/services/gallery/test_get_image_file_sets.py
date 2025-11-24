"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

from byceps.services.gallery import (
    gallery_domain_service,
    gallery_import_service,
)
from byceps.services.gallery.gallery_import_service import ImageFileSet


def test_get_image_file_sets(fs):
    gallery = gallery_domain_service.create_gallery(
        'cozylan', 'cozylan-2025', 'CozyLAN 2025', False
    )

    expected = [
        ImageFileSet(
            full_filename='cozylan-2025_001.jpg',
            full_exists=True,
            preview_filename='cozylan-2025_001_preview.jpg',
            preview_exists=True,
        ),
        ImageFileSet(
            full_filename='cozylan-2025_002.jpg',
            full_exists=True,
            preview_filename='cozylan-2025_002_preview.jpg',
            preview_exists=True,
        ),
        ImageFileSet(
            full_filename='cozylan-2025_003.jpg',
            full_exists=True,
            preview_filename='cozylan-2025_003_preview.jpg',
            preview_exists=True,
        ),
    ]

    for fn in [
        'cozylan-2025_001.jpg',
        'cozylan-2025_001_preview.jpg',
        'cozylan-2025_002.jpg',
        'cozylan-2025_002_preview.jpg',
        'cozylan-2025_003.jpg',
        'cozylan-2025_003_preview.jpg',
        'cozylan-2025_004.gif',  # file extension ignored
    ]:
        fs.create_file(f'./data/brands/cozylan/galleries/cozylan-2025/{fn}')

    actual = gallery_import_service.get_image_file_sets(
        gallery, data_path=Path('./data')
    )

    assert actual == expected
