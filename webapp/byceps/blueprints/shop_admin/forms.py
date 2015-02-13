# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from wtforms import IntegerField, StringField, TextAreaField

from ...util.l10n import LocalizedForm


class ArticleCreateForm(LocalizedForm):
    description = StringField('Beschreibung')
    quantity = IntegerField('Anzahl verfügbar')


class ArticleUpdateForm(LocalizedForm):
    description = StringField('Beschreibung')
    quantity = IntegerField('Anzahl verfügbar')


class OrderCancelForm(LocalizedForm):
    reason = TextAreaField('Begründung')
