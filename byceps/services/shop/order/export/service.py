"""
byceps.services.shop.order.export.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import current_app

from .....util.money import to_two_places
from .....util.templating import load_template

from .. import service as order_service


def export_order_as_xml(order_id):
    """Export the order as an XML document."""
    order = order_service.find_order_with_details(order_id)

    if order is None:
        return None

    order_tuple = order.to_tuple()
    order_items = [item.to_tuple() for item in order.items]

    now = datetime.now()

    context = {
        'order': order_tuple,
        'email_address': order.placed_by.email_address,
        'order_items': order_items,
        'now': now,
        'format_export_amount': _format_export_amount,
        'format_export_datetime': _format_export_datetime,
    }

    xml = _render_template(context)

    return {
        'content': xml,
        'content_type': 'application/xml; charset=iso-8859-1',
    }


def _format_export_amount(amount):
    """Format the monetary amount as required by the export format
    specification.
    """
    quantized = to_two_places(amount)
    return '{:.2f}'.format(quantized)


def _format_export_datetime(dt):
    """Format date and time as required by the export format specification."""
    timezone = current_app.config['SHOP_ORDER_EXPORT_TIMEZONE']
    localized_dt = timezone.localize(dt)

    date_time, utc_offset = localized_dt.strftime('%Y-%m-%dT%H:%M:%S|%z') \
                                        .split('|', 1)

    if len(utc_offset) == 5:
        # Insert colon between hours and minutes.
        utc_offset = utc_offset[:3] + ':' + utc_offset[3:]

    return date_time + utc_offset


def _render_template(context):
    """Load and render export template."""
    path = 'services/shop/order/export/templates/export.xml'
    with current_app.open_resource(path, 'r') as f:
        source = f.read()

    template = load_template(source)
    return template.render(**context)
