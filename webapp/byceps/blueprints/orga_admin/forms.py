# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import SelectField, StringField
from wtforms.validators import Length

from ...util.l10n import LocalizedForm


class MembershipUpdateForm(LocalizedForm):
    orga_team_id = SelectField('Team')
    duties = StringField('Aufgabe')

    def set_orga_team_choices(self, orga_teams):
        choices = [(str(team.id), team.title) for team in orga_teams]
        self.orga_team_id.choices = choices


class OrgaFlagCreateForm(LocalizedForm):
    user_id = StringField('Benutzer-ID')


class OrgaTeamCreateForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])
