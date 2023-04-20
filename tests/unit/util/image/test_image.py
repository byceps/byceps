"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import pytest

from byceps.util.image import read_dimensions
from byceps.util.image.models import Dimensions, ImageType
from byceps.util.image.typeguess import guess_type


IMAGES_PATH = Path('tests/fixtures/images')


@pytest.mark.parametrize(
    ('filename', 'expected'),
    [
        ('image.bmp',                           None          ),
        ('image.gif',                           ImageType.gif ),
        ('image.jpeg',                          ImageType.jpeg),
        ('image.png',                           ImageType.png ),
        ('image.webp',                          ImageType.webp),
        ('image-with-xml-declaration.svg',      ImageType.svg ),
        ('image-without-xml-declaration.svg',   ImageType.svg ),
    ],
)
def test_guess_type(filename, expected):
    with open_image(filename) as f:
        actual = guess_type(f)

    assert actual == expected


@pytest.mark.parametrize(
    ('filename_suffix', 'expected_width', 'expected_height'),
    [
        ('bmp',   7, 11),
        ('gif',  17,  4),
        ('jpeg', 12,  7),
        ('png',   8, 25),
        ('webp',  9, 16),
    ],
)
def test_read_dimensions(filename_suffix, expected_width, expected_height):
    expected = Dimensions(width=expected_width, height=expected_height)

    with open_image_with_suffix(filename_suffix) as f:
        actual = read_dimensions(f)

    assert actual == expected


def open_image_with_suffix(suffix):
    filename = Path('image').with_suffix('.' + suffix)
    return open_image(filename)


def open_image(filename):
    path = IMAGES_PATH / filename
    return path.open(mode='rb')
