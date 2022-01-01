"""
byceps.util.forms
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask_babel import lazy_gettext
from wtforms import Field
from wtforms.widgets import TextInput

from ..services.user import service as user_service
from ..services.user.transfer.models import User


class UserScreenNameField(Field):
    """A field which takes a user screen name and stores the
    corresponding user object.
    """

    widget = TextInput()

    def __init__(self, label=None, validators=None, **kwargs) -> None:
        super().__init__(label, validators, **kwargs)

    def _value(self) -> str:
        if self.raw_data:
            return self.raw_data[0]

        if self.data is not None:
            # As user was found via screen name, the user object's
            # screen name cannot be empty.
            return self.data.screen_name  # type: ignore

        return ''

    def process_data(self, value) -> None:
        if value is None:
            self.data = None
            return

        screen_name = value.strip()
        user = _find_user_by_screen_name(screen_name)
        if user is None:
            self.data = None
            raise ValueError(lazy_gettext('Unknown username'))

        self.data = user

    def process_formdata(self, valuelist) -> None:
        if not valuelist:
            return

        screen_name = valuelist[0].strip()
        user = _find_user_by_screen_name(screen_name)
        if user is None:
            self.data = None
            raise ValueError(lazy_gettext('Unknown username'))

        self.data = user


def _find_user_by_screen_name(screen_name: str) -> Optional[User]:
    return user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )
