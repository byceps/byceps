"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import pytest

from byceps.util.image.models import ImageType
from byceps.util.image.typeguess import guess_type


IMAGES_PATH = Path('tests/fixtures/images')


@pytest.mark.parametrize(
    ('filename', 'expected'),
    [
        ('image.bmp', None),
        ('image.gif', ImageType.gif),
        ('image.jpeg', ImageType.jpeg),
        ('image.png', ImageType.png),
        ('image.webp', ImageType.webp),
        ('image-with-xml-declaration.svg', ImageType.svg),
        ('image-without-xml-declaration.svg', ImageType.svg),
    ],
)
def test_guess_type(filename, expected):
    with open_image(filename) as f:
        actual = guess_type(f)

    assert actual == expected


def open_image(filename):
    path = IMAGES_PATH / filename
    return path.open(mode='rb')
