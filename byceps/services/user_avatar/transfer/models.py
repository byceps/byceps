"""
byceps.services.user_avatar.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
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
