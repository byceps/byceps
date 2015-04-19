# -*- coding: utf-8 -*-

"""
byceps.blueprints.news_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from wtforms import SelectField, StringField

from ...util.l10n import LocalizedForm


class ItemCreateForm(LocalizedForm):
    slug = StringField('Slug')
    snippet_id = SelectField('Snippet')
