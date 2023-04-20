"""
byceps.blueprints.common.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms.validators import ValidationError

from byceps.services.user import screen_name_validator


class ScreenNameValidator:
    """Make sure screen name contains only permitted characters.

    However, do *not* check the length; use WTForms' `Length` for that.
    """

    def __call__(self, form, field):
        if not screen_name_validator.contains_only_valid_chars(field.data):
            special_chars_spaced = ' '.join(screen_name_validator.SPECIAL_CHARS)
            raise ValidationError(
                lazy_gettext(
                    'Contains invalid characters. Allowed are letters, digits, '
                    'and these special charactes: '
                )
                + special_chars_spaced
            )
