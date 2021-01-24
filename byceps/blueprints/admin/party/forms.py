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
        lazy_gettext('Titel'), validators=[Length(min=1, max=40)]
    )
    starts_at = DateTimeField(
        lazy_gettext('Beginn'),
        format='%d.%m.%Y %H:%M',
        validators=[InputRequired()],
    )
    ends_at = DateTimeField(
        lazy_gettext('Ende'),
        format='%d.%m.%Y %H:%M',
        validators=[InputRequired()],
    )
    max_ticket_quantity = IntegerField(
        lazy_gettext('Maximale Anzahl Tickets'), validators=[Optional()]
    )


class CreateForm(_BaseForm):
    id = StringField(lazy_gettext('ID'), validators=[Length(min=1, max=40)])


class UpdateForm(_BaseForm):
    ticket_management_enabled = BooleanField(
        lazy_gettext('Ticketverwaltung geöffnet')
    )
    seat_management_enabled = BooleanField(
        lazy_gettext('Sitzplatzverwaltung geöffnet)')
    )
    canceled = BooleanField(lazy_gettext('abgesagt'))
    archived = BooleanField(lazy_gettext('archiviert'))
