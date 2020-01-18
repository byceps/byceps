"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.email.transfer.models import Sender

from testfixtures.user import create_user_with_detail


@pytest.mark.parametrize('address, name, expected', [
    ('unnamed@example.com', None, 'unnamed@example.com'),
    ('simple@example.com', 'Simple', 'Simple <simple@example.com>'),
    ('mr.pink@example.com', 'Mr. Pink', '"Mr. Pink" <mr.pink@example.com>'),  # quotes name
])
def test_sender_format(address, name, expected):
    sender = Sender(address, name)

    assert sender.format() == expected
