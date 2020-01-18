"""
byceps.blueprints.admin.orga_team.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import SelectField, StringField
from wtforms.validators import Length

from ....util.l10n import LocalizedForm


class OrgaTeamCreateForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])


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
        self.orga_team_id.choices = choices
