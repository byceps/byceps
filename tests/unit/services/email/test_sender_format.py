"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.email.transfer.models import Sender


@pytest.mark.parametrize(
    'address, name, expected',
    [
        ('unnamed@users.test', None, 'unnamed@users.test'),
        ('simple@users.test', 'Simple', 'Simple <simple@users.test>'),
        ('mr.pink@users.test', 'Mr. Pink', '"Mr. Pink" <mr.pink@users.test>'),  # quotes name
    ],
)
def test_sender_format(address, name, expected):
    sender = Sender(address, name)

    assert sender.format() == expected
