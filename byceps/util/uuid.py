"""
byceps.util.uuid
~~~~~~~~~~~~~~~~

UUID generation

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import uuid

from uuid6 import uuid7


def generate_uuid4() -> uuid.UUID:
    """Generate a random UUID (Universally Unique IDentifier), version 4."""
    return uuid.uuid4()


def generate_uuid7() -> uuid.UUID:
    """Generate a random UUID (Universally Unique IDentifier), version 7."""
    return uuid7()
