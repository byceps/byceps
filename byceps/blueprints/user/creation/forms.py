"""
byceps.blueprints.user.creation.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import UUID

from wtforms import BooleanField, HiddenField, PasswordField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from ....services.user import screen_name_validator
from ....util.l10n import LocalizedForm


class ScreenNameValidator:
    """Make sure screen name contains only permitted characters.

    However, do *not* check the length; use WTForms' `Length` for that.
    """

    def __call__(self, form, field):
        if not screen_name_validator.contains_only_valid_chars(field.data):
            special_chars_spaced = ' '.join(screen_name_validator.SPECIAL_CHARS)
            raise ValidationError(
                'Enthält ungültige Zeichen. Erlaubt sind Buchstaben, '
                f' Ziffern und diese Sonderzeichen: {special_chars_spaced}'
            )


class UserCreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
        ScreenNameValidator(),
    ])
    first_names = StringField('Vorname(n)', [InputRequired(), Length(min=2, max=40)])
    last_name = StringField('Nachname', [InputRequired(), Length(min=2, max=80)])
    email_address = StringField('E-Mail-Adresse', [InputRequired(), Length(min=6, max=120)])
    password = PasswordField('Passwort', [InputRequired(), Length(min=8)])
    terms_version_id = HiddenField('AGB-Version', [InputRequired()])
    consent_to_terms = BooleanField('AGB', [InputRequired()])
    consent_to_privacy_policy = BooleanField('Datenschutzbestimmungen', [InputRequired()])
    subscribe_to_newsletter = BooleanField('Newsletter')
    is_bot = BooleanField('Bot')

    @staticmethod
    def validate_terms_version_id(form, field):
        try:
            UUID(field.data)
        except ValueError:
            raise ValueError('Ungültige AGB-Version.')

    @staticmethod
    def validate_is_bot(form, field):
        if field.data:
            raise ValueError('Bots sind nicht erlaubt.')
