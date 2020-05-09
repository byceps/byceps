"""
byceps.services.user.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import Optional

from ....typing import UserID


@dataclass(frozen=True)
class User:
    id: UserID
    screen_name: Optional[str]
    suspended: bool
    deleted: bool
    avatar_url: Optional[str]
    is_orga: bool
