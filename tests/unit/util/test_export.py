"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.export import serialize_to_csv


def test_serialize_to_csv():
    field_names = ['name', 'color']
    rows = [
        {'name': 'Sonic the Hedgehog', 'color': 'blue'},
        {'name': 'Pac-Man', 'color': 'yellow'},
        {'name': 'Ultraman', 'color': 'white/red'},
    ]

    actual = serialize_to_csv(field_names, rows)

    assert list(actual) == [
        'name;color\r\n',
        'Sonic the Hedgehog;blue\r\n',
        'Pac-Man;yellow\r\n',
        'Ultraman;white/red\r\n',
    ]
