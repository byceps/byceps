"""
byceps.blueprints.common.user.creation.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import re
from typing import Set

from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from .....services.consent.transfer.models import Subject, SubjectID
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


class UserCreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
        ScreenNameValidator(),
    ])
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
    def validate_is_bot(form, field):
        if field.data:
            raise ValueError('Bots sind nicht erlaubt.')

    def get_field_for_consent_subject_id(self, subject_id: SubjectID):
        name = _generate_consent_subject_field_name(subject_id)
        return getattr(self, name)


def assemble_user_create_form(
    real_name_required: bool,
    required_consent_subjects: Set[Subject],
    newsletter_offered: bool,
):
    extra_fields = {}

    if real_name_required:
        extra_fields['first_names'] = StringField('Vorname(n)', [InputRequired(), Length(min=2, max=40)])
        extra_fields['last_name'] = StringField('Nachname', [InputRequired(), Length(min=2, max=80)])

    for subject in required_consent_subjects:
        field_name = _generate_consent_subject_field_name(subject.id)
        extra_fields[field_name] = BooleanField('', [InputRequired()])

    if newsletter_offered:
        extra_fields['subscribe_to_newsletter'] = BooleanField('Newsletter')

    # Create a configuration-specific subclass instead of
    # modifying the original shared class.
    subclass_name = UserCreateForm.__name__
    subclass_bases = (UserCreateForm,)
    return type(subclass_name, subclass_bases, extra_fields)


def _generate_consent_subject_field_name(subject_id: SubjectID) -> str:
    return f'consent_to_subject_{subject_id.hex}'
