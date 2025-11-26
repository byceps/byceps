"""
byceps.services.tourney.tourney.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import DateTimeLocalField, IntegerField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from byceps.services.party.models import PartyID
from byceps.services.tourney import tourney_category_service
from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
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
    starts_at = DateTimeLocalField(
        lazy_gettext('Start'), validators=[InputRequired()]
    )

    def set_category_choices(self, party_id: PartyID):
        categories = tourney_category_service.get_categories_for_party(party_id)
        categories.sort(key=lambda category: category.position)
        self.category_id.choices = [
            (category.id, category.title) for category in categories
        ]


class CreateForm(_BaseForm):
    team_size = SelectField(
        lazy_gettext('Team size'),
        [InputRequired()],
        choices=[(value, value) for value in range(1, 17)],
    )


class UpdateForm(_BaseForm):
    pass
