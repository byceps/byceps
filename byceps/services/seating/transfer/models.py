"""
byceps.services.seating.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID


AreaID = NewType('AreaID', UUID)


SeatID = NewType('SeatID', UUID)


SeatGroupID = NewType('SeatGroupID', UUID)
