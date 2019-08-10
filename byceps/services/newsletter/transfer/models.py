"""
byceps.services.newsletter.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from attr import attrs

from ....typing import BrandID, UserID


@attrs(auto_attribs=True, frozen=True, slots=True)
class Subscription:
    user_id: UserID
    brand_id: BrandID
    expressed_at: datetime
