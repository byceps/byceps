"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path

import pytest

from byceps.util.image import read_dimensions
from byceps.util.image.models import Dimensions, ImageType
from byceps.util.image.typeguess import guess_type


@pytest.mark.parametrize('filename_suffix, expected', [
    ('bmp',  None          ),
    ('gif',  ImageType.gif ),
    ('jpeg', ImageType.jpeg),
    ('png',  ImageType.png ),
])
def test_guess_type(filename_suffix, expected):
    with open_image_with_suffix(filename_suffix) as f:
        actual = guess_type(f)

    assert actual == expected


@pytest.mark.parametrize('filename_suffix, expected_width, expected_height', [
    ('bmp',   7, 11),
    ('gif',  17,  4),
    ('jpeg', 12,  7),
    ('png',   8, 25),
])
def test_read_dimensions(filename_suffix, expected_width, expected_height):
    expected = Dimensions(width=expected_width, height=expected_height)

    with open_image_with_suffix(filename_suffix) as f:
        actual = read_dimensions(f)

    assert actual == expected


def open_image_with_suffix(suffix):
    path = Path('testfixtures/images/image').with_suffix('.' + suffix)
    return path.open(mode='rb')
