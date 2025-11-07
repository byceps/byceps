"""
byceps.services.whereabouts.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext, lazy_pgettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired, Optional, ValidationError

from byceps.services.user import user_service
from byceps.services.whereabouts import (
    whereabouts_client_service,
    whereabouts_sound_service,
)
from byceps.util.l10n import LocalizedForm


class ClientUpdateForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [Optional()])
    location = StringField(lazy_gettext('Location'), [Optional()])
    description = StringField(lazy_gettext('Description'), [Optional()])

    @staticmethod
    def validate_name(form, field):
        name = field.data
        if whereabouts_client_service.find_client_by_name(name) is not None:
            raise ValidationError(lazy_gettext('The value is already in use.'))


class WhereaboutsCreateForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [InputRequired()])
    description = StringField(lazy_gettext('Description'), [InputRequired()])
    hidden_if_empty = BooleanField(lazy_gettext('hidden if empty'))
    secret = BooleanField(lazy_pgettext('whereabouts', 'secret'))


def validate_user_screen_name(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(screen_name)

    if user is None:
        raise ValidationError(lazy_gettext('Unknown username'))

    existing_user_sound = whereabouts_sound_service.find_sound_for_user(user.id)
    if existing_user_sound:
        raise ValidationError(
            lazy_gettext('The user already has a sound assigned.')
        )

    field.data = user


class UserSoundCreateForm(LocalizedForm):
    user = StringField(
        lazy_gettext('Username'),
        [InputRequired(), validate_user_screen_name],
    )
    name = StringField(lazy_gettext('Sound name'), [InputRequired()])
