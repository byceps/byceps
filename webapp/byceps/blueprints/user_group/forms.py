# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_group.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import TextAreaField, TextField

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = TextField('Titel')
    description = TextAreaField('Beschreibung')
