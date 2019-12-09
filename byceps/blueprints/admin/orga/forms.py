"""
byceps.blueprints.admin.orga.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ....services.orga import service as orga_service
from ....services.user import service as user_service
from ....util.l10n import LocalizedForm


def validate_user_screen_name(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

    if user is None:
        raise ValidationError('Unbekannter Benutzername')

    orga_flag = orga_service.find_orga_flag(form.brand_id, user.id)
    if orga_flag is not None:
        raise ValidationError('Der Benutzer ist bereits Orga für diese Marke.')

    field.data = user.to_dto()


class OrgaFlagCreateForm(LocalizedForm):

    def __init__(self, *args, brand_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brand_id = brand_id

    user = StringField('Benutzername', [InputRequired(), validate_user_screen_name])
