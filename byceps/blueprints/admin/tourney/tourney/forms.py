"""
byceps.blueprints.admin.tourney.tourney.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import DateField, IntegerField, SelectField, StringField, TimeField
from wtforms.validators import InputRequired, Length, Optional

from .....services.tourney import tourney_category_service
from .....typing import PartyID
from .....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'), [InputRequired(), Length(max=40)]
    )
    subtitle = StringField(
        lazy_gettext('Subtitle'), [Optional(), Length(max=80)]
    )
    logo_url = StringField(
        lazy_gettext('Logo URL'), [Optional(), Length(max=120)]
    )
    category_id = SelectField(
        lazy_gettext('Category'), validators=[InputRequired()]
    )
    max_participant_count = IntegerField(
        lazy_gettext('Maximum number of attendees'), [InputRequired()]
    )
    starts_on = DateField(
        lazy_gettext('Start (date)'), validators=[InputRequired()]
    )
    starts_at = TimeField(
        lazy_gettext('Start (time)'), validators=[InputRequired()]
    )

    def set_category_choices(self, party_id: PartyID):
        categories = tourney_category_service.get_categories_for_party(party_id)
        categories.sort(key=lambda category: category.position)
        self.category_id.choices = [
            (category.id, category.title) for category in categories
        ]


class UpdateForm(CreateForm):
    pass
