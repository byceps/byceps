"""
byceps.blueprints.admin.shop.article.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime, time
from decimal import Decimal

from flask_babel import lazy_gettext, pgettext
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import (
    InputRequired,
    NumberRange,
    Optional,
    ValidationError,
)

from .....util.l10n import LocalizedForm


class _ArticleBaseForm(LocalizedForm):
    description = StringField(
        lazy_gettext('Description'), validators=[InputRequired()]
    )
    price = DecimalField(
        lazy_gettext('Unit price'), places=2, validators=[InputRequired()]
    )
    tax_rate = DecimalField(
        lazy_gettext('Tax rate'),
        places=1,
        validators=[
            InputRequired(),
            NumberRange(min=Decimal('0.0'), max=Decimal('99.9')),
        ],
    )
    total_quantity = IntegerField(
        lazy_gettext('Total quantity'), validators=[InputRequired()]
    )
    max_quantity_per_order = IntegerField(
        lazy_gettext('Maximum quantity per order'),
        validators=[InputRequired()],
    )


class ArticleCreateForm(_ArticleBaseForm):
    article_number_sequence_id = SelectField(
        lazy_gettext('Article number sequence'), validators=[InputRequired()]
    )

    def set_article_number_sequence_choices(self, sequences):
        sequences.sort(key=lambda seq: seq.prefix)

        choices = [(str(seq.id), seq.prefix) for seq in sequences]
        choices.insert(0, ('', pgettext('sequence', '<none>')))
        self.article_number_sequence_id.choices = choices


class ArticleUpdateForm(_ArticleBaseForm):
    available_from_date = DateField(
        lazy_gettext('Available from date'), validators=[Optional()]
    )
    available_from_time = TimeField(
        lazy_gettext('Available from time'), validators=[Optional()]
    )
    available_until_date = DateField(
        lazy_gettext('Available until date'), validators=[Optional()]
    )
    available_until_time = TimeField(
        lazy_gettext('Available until time'), validators=[Optional()]
    )
    not_directly_orderable = BooleanField(
        lazy_gettext('can only be ordered indirectly')
    )
    requires_separate_order = BooleanField(
        lazy_gettext('must be ordered separately')
    )
    shipping_required = BooleanField(lazy_gettext('Shipping required'))

    @staticmethod
    def validate_available_from_date(form, field):
        """Ensure that either both date and time or neither of them is given."""
        d = form.available_from_date.data
        t = form.available_from_time.data
        _validate_date_and_time(d, t)

    @staticmethod
    def validate_available_from_time(form, field):
        """Ensure that either both date and time or neither of them is given."""
        d = form.available_from_date.data
        t = form.available_from_time.data
        _validate_date_and_time(d, t)

    @staticmethod
    def validate_available_until_date(form, field):
        """Ensure that either both date and time or neither of them is given."""
        d = form.available_until_date.data
        t = form.available_until_time.data
        _validate_date_and_time(d, t)

        available_from = form._get_available_from()
        available_until = form._get_available_until()
        _validate_availability_range(available_from, available_until)

    @staticmethod
    def validate_available_until_time(form, field):
        """Ensure that either both date and time or neither of them is given."""
        d = form.available_until_date.data
        t = form.available_until_time.data
        _validate_date_and_time(d, t)

        available_from = form._get_available_from()
        available_until = form._get_available_until()
        _validate_availability_range(available_from, available_until)

    def _get_available_from(self):
        d = self.available_from_date.data
        t = self.available_from_time.data
        if (d is None) or (t is None):
            return None

        return datetime.combine(d, t)

    def _get_available_until(self):
        d = self.available_until_date.data
        t = self.available_until_time.data
        if (d is None) or (t is None):
            return None

        return datetime.combine(d, t)


def _validate_date_and_time(d: date, t: time):
    if ((d is None) and (t is not None)) or ((d is not None) and (t is None)):
        raise ValidationError(
            lazy_gettext(
                'Either date and time must be specified or neither of them.'
            )
        )


def _validate_availability_range(
    available_from: datetime, available_until: datetime
):
    """Ensure that the availability range's begin is before its end."""
    if (
        (available_from is not None)
        and (available_until is not None)
        and (available_from >= available_until)
    ):
        raise ValidationError(
            lazy_gettext(
                'The end of the availability period must be after its begin.'
            )
        )


class ArticleAttachmentCreateForm(LocalizedForm):
    article_to_attach_id = SelectField(
        lazy_gettext('Article'), validators=[InputRequired()]
    )
    quantity = IntegerField(
        lazy_gettext('Quantity'), validators=[InputRequired()]
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
        lazy_gettext('Static prefix'), validators=[InputRequired()]
    )
