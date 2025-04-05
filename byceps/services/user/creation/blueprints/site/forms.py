"""
byceps.services.user.creation.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from byceps.services.consent.models import ConsentSubject, ConsentSubjectID
from byceps.services.core.blueprints.common.forms import ScreenNameValidator
from byceps.services.user import screen_name_validator, user_service
from byceps.util.l10n import LocalizedForm


EMAIL_ADDRESS_PATTERN = re.compile(r'^.+?@.+?\..+?$')


def validate_email_address(form, field):
    if EMAIL_ADDRESS_PATTERN.search(field.data) is None:
        raise ValidationError(lazy_gettext('Invalid email address'))

    if user_service.is_email_address_already_assigned(field.data):
        raise ValidationError(
            lazy_gettext('This email address is not available.')
        )


def validate_screen_name_availability(form, field):
    if user_service.is_screen_name_already_assigned(field.data):
        raise ValidationError(lazy_gettext('This username is not available.'))


class UserCreateForm(LocalizedForm):
    screen_name = StringField(
        lazy_gettext('Username'),
        [
            InputRequired(),
            Length(
                min=screen_name_validator.MIN_LENGTH,
                max=screen_name_validator.MAX_LENGTH,
            ),
            ScreenNameValidator(),
            validate_screen_name_availability,
        ],
    )
    email_address = StringField(
        lazy_gettext('Email address'),
        [InputRequired(), Length(min=6, max=120), validate_email_address],
    )
    password = PasswordField(
        lazy_gettext('Password'), [InputRequired(), Length(min=10)]
    )
    is_bot = BooleanField(lazy_gettext('Bot'))

    @staticmethod
    def validate_is_bot(form, field):
        if field.data:
            raise ValidationError(lazy_gettext('Bots are not permitted.'))

    def get_field_for_consent_subject_id(self, subject_id: ConsentSubjectID):
        name = _generate_consent_subject_field_name(subject_id)
        return getattr(self, name)


def assemble_user_create_form(
    real_name_required: bool,
    required_consent_subjects: set[ConsentSubject],
    newsletter_offered: bool,
):
    extra_fields = {}

    if real_name_required:
        extra_fields['first_name'] = StringField(
            lazy_gettext('First name'),
            [InputRequired(), Length(min=2, max=40)],
        )
        extra_fields['last_name'] = StringField(
            lazy_gettext('Last name'),
            [InputRequired(), Length(min=2, max=80)],
        )

    for subject in required_consent_subjects:
        field_name = _generate_consent_subject_field_name(subject.id)
        extra_fields[field_name] = BooleanField('', [InputRequired()])

    if newsletter_offered:
        extra_fields['subscribe_to_newsletter'] = BooleanField(
            lazy_gettext('Newsletter')
        )

    # Create a configuration-specific subclass instead of
    # modifying the original shared class.
    subclass_name = UserCreateForm.__name__
    subclass_bases = (UserCreateForm,)
    return type(subclass_name, subclass_bases, extra_fields)


def _generate_consent_subject_field_name(subject_id: ConsentSubjectID) -> str:
    return f'consent_to_subject_{subject_id.hex}'
