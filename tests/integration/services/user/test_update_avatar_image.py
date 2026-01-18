"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import pytest

from byceps.services.user import user_avatar_service
from byceps.util.image.image_type import ImageType


@pytest.mark.parametrize(
    ('image_extension', 'image_type'),
    [
        ('jpeg', ImageType.jpeg),
        ('png', ImageType.png),
    ],
)
def test_path(data_path, database, user, image_extension, image_type):
    with Path(f'tests/fixtures/images/image.{image_extension}').open('rb') as f:
        avatar, _ = user_avatar_service.update_avatar_image(
            user, f, {image_type}, user
        ).unwrap()

    expected_filename = f'{avatar.id}.{image_extension}'
    expected = data_path / 'global' / 'users' / 'avatars' / expected_filename

    assert avatar.path == expected
