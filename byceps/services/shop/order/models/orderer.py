"""
byceps.services.shop.order.models.order.orderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs

from .....typing import UserID


@attrs(frozen=True, slots=True)
class Orderer:
    """Someone who orders articles."""

    user_id = attrib(type=UserID)
    first_names = attrib(type=str)
    last_name = attrib(type=str)
    country = attrib(type=str)
    zip_code = attrib(type=str)
    city = attrib(type=str)
    street = attrib(type=str)
