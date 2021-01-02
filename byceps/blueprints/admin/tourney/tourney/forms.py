"""
byceps.blueprints.admin.tourney.tourney.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import SelectField, StringField
from wtforms.fields.html5 import DateField, IntegerField, TimeField
from wtforms.validators import InputRequired, Length, Optional

from .....services.tourney import category_service
from .....typing import PartyID
from .....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField('Titel', [InputRequired(), Length(max=40)])
    subtitle = StringField('Untertitel', [Optional(), Length(max=80)])
    logo_url = StringField('Logo-URL', [Optional(), Length(max=120)])
    category_id = SelectField('Kategorie', validators=[InputRequired()])
    max_participant_count = IntegerField('Maximale Anzahl Teilnehmer', [InputRequired()])
    starts_on = DateField('Beginn (Datum)', validators=[InputRequired()])
    starts_at = TimeField('Beginn (Uhrzeit)', validators=[InputRequired()])

    def set_category_choices(self, party_id: PartyID):
        categories = category_service.get_categories_for_party(party_id)
        categories.sort(key=lambda category: category.position)
        self.category_id.choices = [
            (category.id, category.title) for category in categories
        ]


class UpdateForm(CreateForm):
    pass
