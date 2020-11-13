"""
byceps.blueprints.admin.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from ....util.framework.blueprint import create_blueprint


blueprint = create_blueprint('shop_admin', __name__)


@blueprint.add_app_template_filter
def tax_rate_as_percentage(tax_rate) -> str:
    # Keep a digit after the decimal point in case
    # the tax rate is a fractional number.
    percentage = (tax_rate * 100).quantize(Decimal('.0'))
    return str(percentage).replace('.', ',')
