"""
byceps.services.orga.birthday_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import islice
from typing import Any, Dict, Iterator, Sequence

from ...database import db

from ..user_avatar import service as user_avatar_service
from ..user.models.detail import UserDetail
from ..user.models.user import User

from .models import OrgaFlag


def collect_orgas_with_next_birthdays(*, limit: int=None) \
                                      -> Iterator[Dict[str, Any]]:
    """Yield the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = _collect_orgas_with_birthdays()

    sorted_orgas = sort_users_by_next_birthday(orgas_with_birthdays)

    if limit is not None:
        sorted_orgas = list(islice(sorted_orgas, limit))

    orgas = sorted_orgas

    user_ids = {user.id for user in orgas}

    avatar_urls_by_user_id = user_avatar_service \
        .get_avatar_urls_for_users(user_ids)

    for user in orgas:
        avatar_url = avatar_urls_by_user_id.get(user.id)

        yield {
            'id': user.id,
            'screen_name': user.screen_name,
            'detail': user.detail,
            'avatar_url': avatar_url,
            'is_orga': False,
        }


def _collect_orgas_with_birthdays() -> Sequence[User]:
    """Return all organizers whose birthday is known."""
    return User.query \
        .join(OrgaFlag) \
        .join(UserDetail) \
        .filter(UserDetail.date_of_birth != None) \
        .options(db.joinedload('detail')) \
        .all()


def sort_users_by_next_birthday(users: Sequence[User]) -> Sequence[User]:
    return sorted(users,
                  key=lambda user: (
                    user.detail.days_until_next_birthday,
                    -user.detail.age))
