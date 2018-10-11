"""
byceps.services.user.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs

from ....typing import UserID


@attrs(frozen=True, slots=True)
class User:
    id = attrib(type=UserID)
    screen_name = attrib(type=str)
    suspended = attrib(type=bool)
    deleted = attrib(type=bool)
    avatar_url = attrib(type=str)
    is_orga = attrib(type=bool)
