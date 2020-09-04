"""
byceps.blueprints.common.user.creation.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import re
from uuid import UUID

from wtforms import BooleanField, HiddenField, PasswordField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from .....services.user import screen_name_validator
from .....services.user import service as user_service
from .....util.l10n import LocalizedForm


EMAIL_ADDRESS_PATTERN = re.compile(r'^.+?@.+?\..+?$')


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


def assemble_user_create_form(
    real_name_required: bool,
    terms_consent_required: bool,
    privacy_policy_consent_required: bool,
    newsletter_offered: bool,
):
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
        is_bot = BooleanField('Bot')

        @staticmethod
        def validate_screen_name(form, field):
            if user_service.is_screen_name_already_assigned(field.data):
                raise ValueError('Dieser Benutzername kann nicht verwendet werden.')

        @staticmethod
        def validate_email_address(form, field):
            if EMAIL_ADDRESS_PATTERN.search(field.data) is None:
                raise ValueError('Die E-Mail-Adresse ist ungültig.')

            if user_service.is_email_address_already_assigned(field.data):
                raise ValueError(
                    'Diese E-Mail-Adresse kann nicht verwendet werden.'
                )

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

    if not real_name_required:
        del UserCreateForm.first_names
        del UserCreateForm.last_name

    if terms_consent_required:
        terms_version_id = HiddenField('AGB-Version', [InputRequired()])
        consent_to_terms = BooleanField('AGB', [InputRequired()])
        setattr(UserCreateForm, 'terms_version_id', terms_version_id)
        setattr(UserCreateForm, 'consent_to_terms', consent_to_terms)

    if privacy_policy_consent_required:
        consent_to_privacy_policy = BooleanField('Datenschutzbestimmungen', [InputRequired()])
        setattr(UserCreateForm, 'consent_to_privacy_policy', consent_to_privacy_policy)

    if newsletter_offered:
        subscribe_to_newsletter = BooleanField('Newsletter')
        setattr(UserCreateForm, 'subscribe_to_newsletter', subscribe_to_newsletter)

    return UserCreateForm
