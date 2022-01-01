"""
byceps.blueprints.admin.ticketing.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ....services.ticketing import ticket_code_service
from ....util.forms import UserScreenNameField
from ....util.l10n import LocalizedForm


class UpdateCodeForm(LocalizedForm):
    code = StringField(lazy_gettext('Code'), [InputRequired()])

    @staticmethod
    def validate_code(form, field):
        if not ticket_code_service.is_ticket_code_wellformed(field.data):
            raise ValidationError(lazy_gettext('Invalid format'))


class SpecifyUserForm(LocalizedForm):
    user = UserScreenNameField(lazy_gettext('Username'), [InputRequired()])
