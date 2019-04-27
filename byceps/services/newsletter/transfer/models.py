"""
byceps.services.newsletter.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from attr import attrib, attrs

from ....typing import BrandID, UserID


@attrs(frozen=True, slots=True)
class Subscription:
    user_id = attrib(type=UserID)
    brand_id = attrib(type=BrandID)
    expressed_at = attrib(type=datetime)
