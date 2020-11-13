"""
byceps.blueprints.admin.orga_team.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import SelectField, StringField
from wtforms.validators import Length

from ....util.l10n import LocalizedForm


class OrgaTeamCreateForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])


class OrgaTeamsCopyForm(LocalizedForm):
    party_id = SelectField('Von Party')

    def set_party_choices(self, parties, team_count_per_party=None):
        def get_label(party):
            label = party.title
            if team_count_per_party:
                team_count = team_count_per_party.get(party.id, 0)
                label += f' ({team_count:d} Teams)'
            return label

        choices = [(party.id, get_label(party)) for party in parties]

        self.party_id.choices = choices


class MembershipFormBase(LocalizedForm):
    duties = StringField('Aufgabe')


class MembershipCreateForm(MembershipFormBase):
    user_id = SelectField('Benutzer')

    def set_user_choices(self, orgas):
        choices = [(str(orga.id), orga.screen_name) for orga in orgas]
        self.user_id.choices = choices


class MembershipUpdateForm(MembershipFormBase):
    orga_team_id = SelectField('Team')

    def set_orga_team_choices(self, orga_teams):
        choices = [(str(team.id), team.title) for team in orga_teams]
        choices.sort(key=lambda t: t[1])
        self.orga_team_id.choices = choices
