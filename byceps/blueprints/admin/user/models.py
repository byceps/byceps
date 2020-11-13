"""
byceps.blueprints.admin.user.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from ....services.user.transfer.models import User


UserStateFilter = Enum('UserStateFilter', [
    'none',
    'active',
    'uninitialized',
    'suspended',
    'deleted',
])


@dataclass(frozen=True)
class UserWithCreationDetails(User):
    created_at: datetime
    initialized: bool
    detail: 'Detail'


@dataclass(frozen=True)
class Detail:
    full_name: Optional[str]
