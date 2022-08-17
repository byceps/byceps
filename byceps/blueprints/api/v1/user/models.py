"""
byceps.blueprints.api.v1.user.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pydantic import BaseModel


class InvalidateEmailAddressRequest(BaseModel):
    email_address: str
    reason: str
