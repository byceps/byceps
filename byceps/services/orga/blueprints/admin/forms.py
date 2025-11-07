"""
byceps.services.orga.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from byceps.services.orga import orga_service
from byceps.services.user import user_service
from byceps.util.l10n import LocalizedForm


class GrantOrgaStatusForm(LocalizedForm):
    def __init__(self, *args, brand_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brand_id = brand_id

    user = StringField(lazy_gettext('Username'), [InputRequired()])

    @staticmethod
    def validate_user(form, field):
        screen_name = field.data.strip()

        user = user_service.find_user_by_screen_name(screen_name)

        if user is None:
            raise ValidationError(lazy_gettext('Unknown username'))

        if orga_service.has_orga_status(user.id, form.brand_id):
            raise ValidationError(
                lazy_gettext(
                    'The user already has organizer status for this brand.'
                )
            )

        field.data = user
