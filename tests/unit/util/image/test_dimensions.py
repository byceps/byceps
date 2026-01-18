"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import pytest

from byceps.util.image.dimensions import Dimensions, read_dimensions


IMAGES_PATH = Path('tests/fixtures/images')


@pytest.mark.parametrize(
    ('width', 'height', 'expected'),
    [
        (1, 1, True),
        (12, 16, False),
        (16, 12, False),
        (16, 16, True),
    ],
)
def test_is_square(width, height, expected):
    dimensions = Dimensions(width, height)

    assert dimensions.is_square == expected


@pytest.mark.parametrize(
    ('filename_suffix', 'expected_width', 'expected_height'),
    [
        ('bmp', 7, 11),
        ('gif', 17, 4),
        ('jpeg', 12, 7),
        ('png', 8, 25),
        ('webp', 9, 16),
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
