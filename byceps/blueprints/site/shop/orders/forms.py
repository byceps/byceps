"""
byceps.blueprints.site.shop.orders.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import TextAreaField
from wtforms.validators import InputRequired, Length

from .....util.l10n import LocalizedForm


class CancelForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(min=10, max=1000)])
