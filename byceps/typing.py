"""
byceps.typing
~~~~~~~~~~~~~

BYCEPS-specific type aliases for PEP 484 type hints

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import NewType
from uuid import UUID


UserID = NewType('UserID', UUID)

BrandID = NewType('BrandID', str)

PartyID = NewType('PartyID', str)
