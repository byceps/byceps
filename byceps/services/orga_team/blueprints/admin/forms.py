"""
byceps.services.orga_team.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length

from byceps.util.l10n import LocalizedForm


class OrgaTeamCreateForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )


class OrgaTeamsCopyForm(LocalizedForm):
    party_id = SelectField(lazy_gettext('From party'), [InputRequired()])

    def set_party_choices(self, parties, team_count_per_party=None):
        def get_label(party):
            label = party.title
            if team_count_per_party:
                team_count = team_count_per_party.get(party.id, 0)
                label += lazy_gettext(
                    ' (%(team_count)s teams)', team_count=team_count
                )
            return label

        choices = [(party.id, get_label(party)) for party in parties]

        self.party_id.choices = choices


class MembershipFormBase(LocalizedForm):
    duties = StringField(lazy_gettext('Function'))


class MembershipCreateForm(MembershipFormBase):
    user_id = SelectField(lazy_gettext('User'), [InputRequired()])

    def set_user_choices(self, orgas):
        choices = [(str(orga.id), orga.screen_name) for orga in orgas]
        self.user_id.choices = choices


class MembershipUpdateForm(MembershipFormBase):
    orga_team_id = SelectField(lazy_gettext('Team'), [InputRequired()])

    def set_orga_team_choices(self, orga_teams):
        choices = [(str(team.id), team.title) for team in orga_teams]
        choices.sort(key=lambda t: t[1])
        self.orga_team_id.choices = choices
