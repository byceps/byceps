"""
byceps.blueprints.admin.shop.sold_products.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired

from byceps.util.l10n import LocalizedForm


class GenerateForm(LocalizedForm):
    product_number1 = StringField(
        lazy_gettext('Product number'), validators=[InputRequired()]
    )
    product_number2 = StringField(lazy_gettext('Product number'))
    product_number3 = StringField(lazy_gettext('Product number'))
    product_number4 = StringField(lazy_gettext('Product number'))
