# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import Length

from ...util.l10n import LocalizedForm


class MembershipUpdateForm(LocalizedForm):
    duties = StringField('Aufgabe')


class OrgaFlagCreateForm(LocalizedForm):
    user_id = StringField('Benutzer-ID')


class OrgaTeamCreateForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])
