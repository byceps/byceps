"""
byceps.services.authn.identity_tag.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired, Optional, ValidationError

from byceps.services.user import user_service
from byceps.services.authn.identity_tag import authn_identity_tag_service
from byceps.util.l10n import LocalizedForm


def validate_user_screen_name(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(screen_name)

    if user is None:
        raise ValidationError(lazy_gettext('Unknown username'))

    field.data = user


class CreateForm(LocalizedForm):
    identifier = StringField(lazy_gettext('Identifier'), [InputRequired()])
    user = StringField(
        lazy_gettext('Username'),
        [InputRequired(), validate_user_screen_name],
    )
    note = StringField(lazy_gettext('Note'), [Optional()])
    suspended = BooleanField(lazy_gettext('suspended'))

    @staticmethod
    def validate_identifier(form, field):
        identifier = field.data.strip()

        tag = authn_identity_tag_service.find_tag_by_identifier(identifier)
        if tag:
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )
