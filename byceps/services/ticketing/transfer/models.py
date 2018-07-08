"""
byceps.services.ticketing.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID


TicketCategoryID = NewType('TicketCategoryID', UUID)


TicketCode = NewType('TicketCode', str)


TicketID = NewType('TicketID', UUID)


TicketBundleID = NewType('TicketBundleID', UUID)
