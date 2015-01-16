# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from wtforms import IntegerField, StringField

from ...util.l10n import LocalizedForm


class ArticleUpdateForm(LocalizedForm):
    item_number = StringField('Artikelnummer')
    description = StringField('Beschreibung')
    quantity = IntegerField('Anzahl verfügbar')
