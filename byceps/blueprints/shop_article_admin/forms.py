# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_article_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, DecimalField, IntegerField, SelectField, \
    StringField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class ArticleCreateForm(LocalizedForm):
    description = StringField('Beschreibung')
    price = DecimalField('Stückpreis', places=2, validators=[InputRequired()])
    tax_rate = DecimalField('Steuersatz', places=3, validators=[InputRequired()])
    quantity = IntegerField('Anzahl verfügbar', validators=[InputRequired()])


class ArticleUpdateForm(ArticleCreateForm):
    max_quantity_per_order = IntegerField('Maximale Anzahl pro Bestellung')
    not_directly_orderable = BooleanField('nur indirekt bestellbar')
    requires_separate_order = BooleanField('muss separat bestellt werden')


class ArticleAttachmentCreateForm(LocalizedForm):
    article_to_attach_id = SelectField('Artikel', validators=[InputRequired()])
    quantity = IntegerField('Anzahl', validators=[InputRequired()])

    def set_article_to_attach_choices(self, attachable_articles):
        def to_label(article):
            return '{} – {}'.format(article.item_number, article.description)

        choices = [(str(article.id), to_label(article))
                   for article in attachable_articles]

        self.article_to_attach_id.choices = choices
