"""
byceps.blueprints.admin.party.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, IntegerField, StringField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import InputRequired, Length, Optional

from ....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )
    starts_on = DateField(lazy_gettext('Start date'), validators=[InputRequired()])
    starts_at = TimeField(lazy_gettext('Start time'), validators=[InputRequired()])
    ends_on = DateField(lazy_gettext('End date'), validators=[InputRequired()])
    ends_at = TimeField(lazy_gettext('End time'), validators=[InputRequired()])
    max_ticket_quantity = IntegerField(
        lazy_gettext('Maximum number of tickets'), validators=[Optional()]
    )


class CreateForm(_BaseForm):
    id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )


class UpdateForm(_BaseForm):
    ticket_management_enabled = BooleanField(
        lazy_gettext('Ticket management open')
    )
    seat_management_enabled = BooleanField(
        lazy_gettext('Seat management open')
    )
    canceled = BooleanField(lazy_gettext('canceled'))
    archived = BooleanField(lazy_gettext('archived'))
