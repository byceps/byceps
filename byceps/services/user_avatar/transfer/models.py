"""
byceps.services.user_avatar.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID


AvatarID = NewType('AvatarID', UUID)


@dataclass(frozen=True)
class AvatarUpdate:
    occurred_at: datetime
    url_path: str
