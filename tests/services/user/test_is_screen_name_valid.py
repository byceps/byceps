"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import screen_name_validator


@pytest.mark.parametrize('screen_name, expected', [
    ('   '            , False),
    ('byceps'         , True),
    ('Gemüsebrätwürßt', True ),
    ('not@llowed'     , False),  # `@` is denied
    ('Быцепс'         , False),  # Cyrillic letters denied
])
def test_is_screen_name_valid(screen_name, expected):
    assert screen_name_validator.is_screen_name_valid(screen_name) == expected
