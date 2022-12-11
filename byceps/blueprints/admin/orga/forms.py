"""
byceps.blueprints.admin.orga.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ....services.orga import orga_service
from ....services.user import user_service
from ....util.l10n import LocalizedForm


def validate_user_screen_name(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

    if user is None:
        raise ValidationError(lazy_gettext('Unknown username'))

    orga_flag = orga_service.find_orga_flag(form.brand_id, user.id)
    if orga_flag is not None:
        raise ValidationError(
            lazy_gettext('The user already is an organizer for this brand.')
        )

    field.data = user


class OrgaFlagCreateForm(LocalizedForm):
    def __init__(self, *args, brand_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brand_id = brand_id

    user = StringField(
        lazy_gettext('Username'),
        [InputRequired(), validate_user_screen_name],
    )
