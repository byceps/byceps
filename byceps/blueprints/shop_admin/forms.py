# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, DecimalField, IntegerField, SelectField, \
    StringField, TextAreaField

from ...util.l10n import LocalizedForm


class ArticleCreateForm(LocalizedForm):
    description = StringField('Beschreibung')
    price = DecimalField('Stückpreis', places=2)
    tax_rate = DecimalField('Steuersatz', places=3)
    quantity = IntegerField('Anzahl verfügbar')


class ArticleUpdateForm(ArticleCreateForm):
    max_quantity_per_order = IntegerField('Maximale Anzahl pro Bestellung')
    not_directly_orderable = BooleanField('nur indirekt bestellbar')
    requires_separate_order = BooleanField('muss separat bestellt werden')


class ArticleAttachmentCreateForm(LocalizedForm):
    article_to_attach_id = SelectField('Artikel')
    quantity = IntegerField('Anzahl')


class OrderCancelForm(LocalizedForm):
    reason = TextAreaField('Begründung')
