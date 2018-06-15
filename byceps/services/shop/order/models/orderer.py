"""
byceps.services.shop.order.models.order.orderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .....typing import UserID


class Orderer:
    """Someone who orders articles."""

    def __init__(self, user_id: UserID, first_names: str, last_name: str,
                 country: str, zip_code: str, city: str, street: str) -> None:
        self.user_id = user_id
        self.first_names = first_names
        self.last_name = last_name
        self.country = country
        self.zip_code = zip_code
        self.city = city
        self.street = street
