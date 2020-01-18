"""
byceps.util.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import List


def create_permission_enum(key: str, member_names: List[str]) -> Enum:
    """Create a permission enum."""
    name = derive_name(key)

    permission_enum = Enum(name, list(member_names))
    permission_enum.__key__ = key
    permission_enum.__repr__ = lambda self: f'<{self}>'

    return permission_enum


def derive_name(key: str) -> str:
    """Derive a `CamelCase` name from the `underscore_separated_key`."""
    words = key.split('_')
    words.append('permission')

    return ''.join(word.title() for word in words)
