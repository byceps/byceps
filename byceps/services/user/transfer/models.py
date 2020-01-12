"""
byceps.services.user.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from attr import attrs

from ....typing import UserID


@attrs(auto_attribs=True, frozen=True, slots=True)
class User:
    id: UserID
    screen_name: str
    suspended: bool
    deleted: bool
    avatar_url: Optional[str]
    is_orga: bool
