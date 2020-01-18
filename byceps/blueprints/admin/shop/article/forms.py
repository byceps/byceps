"""
byceps.blueprints.admin.shop.article.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import (
    BooleanField,
    DateTimeField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.validators import InputRequired, Optional, ValidationError

from .....util.l10n import LocalizedForm


class ArticleCreateForm(LocalizedForm):
    description = StringField('Beschreibung')
    price = DecimalField('Stückpreis', places=2, validators=[InputRequired()])
    tax_rate = DecimalField('Steuersatz', places=3, validators=[InputRequired()])
    quantity = IntegerField('Anzahl verfügbar', validators=[InputRequired()])


class ArticleUpdateForm(ArticleCreateForm):
    available_from = DateTimeField('Verfügbar ab', format='%d.%m.%Y %H:%M', validators=[Optional()])
    available_until = DateTimeField('Verfügbar bis', format='%d.%m.%Y %H:%M', validators=[Optional()])
    max_quantity_per_order = IntegerField('maximale Anzahl pro Bestellung', validators=[Optional()])
    not_directly_orderable = BooleanField('nur indirekt bestellbar')
    requires_separate_order = BooleanField('muss separat bestellt werden')
    shipping_required = BooleanField('Versand erforderlich')

    @staticmethod
    def validate_available_until(form, field):
        """Ensure that the availability range's begin is before its end."""
        begin = form.available_from.data
        end = field.data

        if (begin is not None) and (begin >= end):
            raise ValidationError(
                'Das Ende des Verfügbarkeitszeitraums muss nach dessen Beginn '
                'liegen.'
            )


class ArticleAttachmentCreateForm(LocalizedForm):
    article_to_attach_id = SelectField('Artikel', validators=[InputRequired()])
    quantity = IntegerField('Anzahl', validators=[InputRequired()])

    def set_article_to_attach_choices(self, attachable_articles):
        def to_label(article):
            return f'{article.item_number} – {article.description}'

        choices = [
            (str(article.id), to_label(article))
            for article in attachable_articles
        ]

        self.article_to_attach_id.choices = choices
