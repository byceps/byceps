"""
byceps.blueprints.admin.party.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask_babel import gettext, lazy_gettext, lazy_pgettext
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    StringField,
    TimeField,
)
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from ....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )
    starts_on = DateField(
        lazy_gettext('Start date'), validators=[InputRequired()]
    )
    starts_at = TimeField(
        lazy_gettext('Start time'), validators=[InputRequired()]
    )
    ends_on = DateField(lazy_gettext('End date'), validators=[InputRequired()])
    ends_at = TimeField(lazy_gettext('End time'), validators=[InputRequired()])
    max_ticket_quantity = IntegerField(
        lazy_gettext('Maximum number of tickets'), validators=[Optional()]
    )

    @staticmethod
    def validate_ends_at(form, field):
        """Ensure that the party starts before it ends."""
        starts_at = datetime.combine(form.starts_on.data, form.starts_at.data)
        ends_at = datetime.combine(form.ends_on.data, form.ends_at.data)

        if starts_at >= ends_at:
            raise ValidationError(
                gettext('The party must begin before it ends.')
            )


class CreateForm(_BaseForm):
    id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )


class UpdateForm(_BaseForm):
    ticket_management_enabled = BooleanField(
        lazy_gettext('Ticket management open')
    )
    seat_management_enabled = BooleanField(lazy_gettext('Seat management open'))
    canceled = BooleanField(lazy_pgettext('party', 'canceled'))
    archived = BooleanField(lazy_gettext('archived'))
