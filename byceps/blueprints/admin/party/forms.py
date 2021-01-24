"""
byceps.blueprints.admin.party.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, DateTimeField, IntegerField, StringField
from wtforms.validators import InputRequired, Length, Optional

from ....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'), validators=[Length(min=1, max=40)]
    )
    starts_at = DateTimeField(
        lazy_gettext('Start'),
        format='%d.%m.%Y %H:%M',
        validators=[InputRequired()],
    )
    ends_at = DateTimeField(
        lazy_gettext('End'),
        format='%d.%m.%Y %H:%M',
        validators=[InputRequired()],
    )
    max_ticket_quantity = IntegerField(
        lazy_gettext('Maximum number of tickets'), validators=[Optional()]
    )


class CreateForm(_BaseForm):
    id = StringField(lazy_gettext('ID'), validators=[Length(min=1, max=40)])


class UpdateForm(_BaseForm):
    ticket_management_enabled = BooleanField(
        lazy_gettext('Ticket management open')
    )
    seat_management_enabled = BooleanField(
        lazy_gettext('Seat management open')
    )
    canceled = BooleanField(lazy_gettext('canceled'))
    archived = BooleanField(lazy_gettext('archived'))
