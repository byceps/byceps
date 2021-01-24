"""
byceps.blueprints.admin.shop.article.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from flask_babel import lazy_gettext
from wtforms import (
    BooleanField,
    DateTimeField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.validators import (
    InputRequired,
    NumberRange,
    Optional,
    ValidationError,
)

from .....util.l10n import LocalizedForm


class _ArticleBaseForm(LocalizedForm):
    description = StringField(lazy_gettext('Beschreibung'))
    price = DecimalField(
        lazy_gettext('Stückpreis'), places=2, validators=[InputRequired()]
    )
    tax_rate = DecimalField(
        lazy_gettext('Steuersatz'),
        places=1,
        validators=[
            InputRequired(),
            NumberRange(min=Decimal('0.0'), max=Decimal('99.9')),
        ],
    )
    total_quantity = IntegerField(
        lazy_gettext('Gesamtmenge'), validators=[InputRequired()]
    )
    max_quantity_per_order = IntegerField(
        lazy_gettext('Maximale Anzahl pro Bestellung'),
        validators=[InputRequired()],
    )


class ArticleCreateForm(_ArticleBaseForm):
    article_number_sequence_id = SelectField(
        lazy_gettext('Artikelnummer-Sequenz'), validators=[InputRequired()]
    )

    def set_article_number_sequence_choices(self, sequences):
        sequences.sort(key=lambda seq: seq.prefix)

        choices = [(str(seq.id), seq.prefix) for seq in sequences]
        choices.insert(0, ('', lazy_gettext('<keine>')))
        self.article_number_sequence_id.choices = choices


class ArticleUpdateForm(_ArticleBaseForm):
    available_from = DateTimeField(
        lazy_gettext('Verfügbar ab'),
        format='%d.%m.%Y %H:%M',
        validators=[Optional()],
    )
    available_until = DateTimeField(
        lazy_gettext('Verfügbar bis'),
        format='%d.%m.%Y %H:%M',
        validators=[Optional()],
    )
    not_directly_orderable = BooleanField(
        lazy_gettext('nur indirekt bestellbar')
    )
    requires_separate_order = BooleanField(
        lazy_gettext('muss separat bestellt werden')
    )
    shipping_required = BooleanField(lazy_gettext('Versand erforderlich'))

    @staticmethod
    def validate_available_until(form, field):
        """Ensure that the availability range's begin is before its end."""
        begin = form.available_from.data
        end = field.data

        if (begin is not None) and (begin >= end):
            raise ValidationError(
                lazy_gettext(
                    'Das Ende des Verfügbarkeitszeitraums muss nach dessen Beginn '
                    'liegen.'
                )
            )


class ArticleAttachmentCreateForm(LocalizedForm):
    article_to_attach_id = SelectField(
        lazy_gettext('Artikel'), validators=[InputRequired()]
    )
    quantity = IntegerField(
        lazy_gettext('Anzahl'), validators=[InputRequired()]
    )

    def set_article_to_attach_choices(self, attachable_articles):
        def to_label(article):
            return f'{article.item_number} – {article.description}'

        choices = [
            (str(article.id), to_label(article))
            for article in attachable_articles
        ]
        choices.sort(key=lambda choice: choice[1])

        self.article_to_attach_id.choices = choices


class ArticleNumberSequenceCreateForm(LocalizedForm):
    prefix = StringField(
        lazy_gettext('Statisches Präfix'), validators=[InputRequired()]
    )
