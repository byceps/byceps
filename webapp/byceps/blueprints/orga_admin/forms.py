# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from wtforms import StringField

from ...util.l10n import LocalizedForm


class MembershipUpdateForm(LocalizedForm):
    duties = StringField('Aufgabe')


class OrgaFlagCreateForm(LocalizedForm):
    user_id = StringField('Benutzer-ID')
