"""
byceps.services.shop.order.export.order_export_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from flask import current_app

from .....services.user import user_service
from .....util.templating import load_template

from .. import order_service
from ..transfer.order import Order, OrderID


def export_order_as_xml(order_id: OrderID) -> Optional[dict[str, str]]:
    """Export the order as an XML document."""
    order = order_service.find_order_with_details(order_id)

    if order is None:
        return None

    context = _assemble_context(order)
    xml = _render_template(context)

    return {
        'content': xml,
        'content_type': 'application/xml; charset=iso-8859-1',
    }


def _assemble_context(order: Order) -> dict[str, Any]:
    """Assemble template context."""
    placed_by = user_service.get_user(order.placed_by_id)
    email_address = user_service.get_email_address(placed_by.id)

    now = datetime.utcnow()

    return {
        'order': order,
        'email_address': email_address,
        'line_items': order.line_items,
        'now': now,
        'format_export_amount': _format_export_amount,
        'format_export_datetime': _format_export_datetime,
    }


def _format_export_amount(amount: Decimal) -> str:
    """Format the monetary amount as required by the export format
    specification.
    """
    # Quantize to two decimal places.
    quantized = amount.quantize(Decimal('.00'))

    return f'{quantized:.2f}'


def _format_export_datetime(dt: datetime) -> str:
    """Format date and time as required by the export format specification."""
    export_tz = ZoneInfo(current_app.config['SHOP_ORDER_EXPORT_TIMEZONE'])
    dt_utc = dt.replace(tzinfo=timezone.utc)
    dt_local = dt_utc.astimezone(export_tz)
    return dt_local.isoformat()


def _render_template(context: dict[str, Any]) -> str:
    """Load and render export template."""
    path = 'services/shop/order/export/templates/export.xml'
    with current_app.open_resource(path, 'r') as f:
        source = f.read()

    template = load_template(source)
    return template.render(**context)
