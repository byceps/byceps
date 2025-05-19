"""
byceps.services.shop.invoice.invoiceninja_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jan Korneffel, Jochen Kupperschmidt, Micha Ober
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from httpx import Client
from moneyed import Money
from urllib.parse import urljoin

from byceps.config.models import InvoiceNinjaConfig
from byceps.services.shop.invoice import order_invoice_service
from byceps.services.shop.invoice.errors import (
    InvoiceDeniedForFreeOrderError,
    InvoiceDownloadError,
    InvoiceError,
    InvoiceProviderNotEnabledError,
)
from byceps.services.shop.invoice.models import DownloadableInvoice
from byceps.services.shop.order import order_log_service
from byceps.services.shop.order.models.detailed_order import AdminDetailedOrder
from byceps.services.shop.order.models.order import LineItem, OrderID
from byceps.services.user import user_command_service, user_service
from byceps.services.user.models.user import User, UserID
from byceps.util.result import Err, Ok, Result


@dataclass(frozen=True)
class InvoiceNinjaInvoice:
    id: str
    invitation_key: str
    paid_to_date: float
    client_id: str
    number: str | None


def get_downloadable_invoice_for_order(
    order: AdminDetailedOrder,
    draft: bool,
    initiator: User,
    config: InvoiceNinjaConfig,
) -> Result[DownloadableInvoice, InvoiceError]:
    """Get a downloadable invoice for the order.

    Create it if it does not exist.
    """
    if order.payment_method == 'free':
        return Err(InvoiceDeniedForFreeOrderError())

    if not config.enabled:
        return Err(InvoiceProviderNotEnabledError())

    client = InvoiceNinjaHttpClient(config)

    invoice = client.get_or_create_invoice(order)

    # If no draft is requested finalize the invoice.
    if not draft:
        # Mark invoice paid if order is already paid.
        # (This also creates an invoice number if the invoice is still
        # in "draft" status.)
        if order.is_paid and invoice.paid_to_date == 0:
            client.create_payment(
                invoice.client_id, invoice.id, order.total_amount
            )

        # If the invoice has no number, it is currently in "draft" status.
        # Marking the invoice as sent creates an invoice number.
        # (If a payment was created previously, `mark_sent` will do
        # nothing, but we still want to record the created invoice number.)
        if not invoice.number:
            invoice_number, download_url = client.mark_sent(invoice.id)
            order_invoice_service.add_invoice(
                order.id, initiator, invoice_number, url=download_url
            )

    return client.download_invoice(invoice.invitation_key).map_err(lambda e: e)


class InvoiceNinjaHttpClient:
    def __init__(self, config: InvoiceNinjaConfig) -> None:
        self._base_url = config.base_url + '/api/v1/'

        self._client = Client()
        self._client.headers['X-Api-Token'] = config.api_key
        self._client.headers['X-Requested-With'] = 'XMLHttpRequest'

    def get_or_create_invoice(
        self, order: AdminDetailedOrder
    ) -> InvoiceNinjaInvoice:
        invoice = self.find_invoice_by_order_number(order.order_number)
        if invoice is not None:
            return invoice

        # Get/create Invoice Ninja customer id and update address.
        customer_id = self.get_customer_id_with_update(order)

        return self.create_invoice(customer_id, order)

    def find_invoice_by_order_number(
        self, order_number: str
    ) -> InvoiceNinjaInvoice | None:
        """Find invoice in Invoice Ninja and return id and paid_to_date."""
        url = self._build_url(
            f'invoices?is_deleted=false&filter={order_number}'
        )
        response = self._client.get(url)
        response_body = response.json()

        data = response_body.get('data')
        if not data:
            return None

        invoice_data = data[0]
        return _transform_invoice_response(invoice_data)

    def get_customer_id_with_update(self, order: AdminDetailedOrder) -> str:
        """Return customer id for orderer, create customer object if necessary."""
        customer_id = _get_user_invoiceninja_customer_id(order.placed_by.id)

        client_data = _fill_client_data(order.placed_by, order)

        if not customer_id:
            customer_id = self._create_client(client_data)
            user_command_service.set_user_detail_extra(
                order.placed_by.id, 'invoiceninja_id', customer_id
            )
        else:
            self._update_client(customer_id, client_data)

        return customer_id

    def _create_client(self, client_data) -> str:
        """Create Invoice Ninja client."""
        url = self._build_url('clients')
        response = self._client.post(url, json=client_data)
        response_body = response.json()

        return response_body['data']['id']

    def _update_client(self, client_id: str, client_data) -> None:
        """Update client address."""
        url = self._build_url(f'clients/{client_id}')
        response = self._client.put(url, json=client_data)
        response.json()

    def create_invoice(
        self, customer_id: str, order: AdminDetailedOrder
    ) -> InvoiceNinjaInvoice:
        """Create invoice."""
        url = self._build_url('invoices')
        data = _assemble_invoice_creation_request_data(customer_id, order)

        response = self._client.post(url, json=data)
        invoice_data = response.json().get('data')

        return _transform_invoice_response(invoice_data)

    def create_payment(
        self, customer_id: str, invoice_id: str, pay_amount: Money
    ) -> None:
        """Create payment."""
        url = self._build_url('payments')
        data = {
            'client_id': customer_id,
            'invoices': [
                {
                    'invoice_id': invoice_id,
                    'amount': str(pay_amount.amount),
                }
            ],
        }

        self._client.post(url, json=data)

    def mark_sent(self, invoice_id: str) -> tuple[str, str]:
        """Set sent flag, which will create an invoice number."""
        url = self._build_url(f'invoices/{invoice_id}/mark_sent')
        response = self._client.get(url)
        invoice = response.json().get('data')

        invoice_number = invoice['number']
        invoice_link = invoice['invitations'][0]['link']

        # `silent=true` prevents the invoice from being marked as "viewed".
        download_url = f'{invoice_link}?silent=true'

        return invoice_number, download_url

    def download_invoice(
        self, invitation_key: str
    ) -> Result[DownloadableInvoice, InvoiceDownloadError]:
        """Download invoice from Invoice Ninja."""
        url = self._build_url(f'invoice/{invitation_key}/download')
        response = self._client.get(url, timeout=10.0)
        if response.status_code != 200:
            return Err(InvoiceDownloadError())

        return Ok(
            DownloadableInvoice(
                content_disposition=response.headers['Content-Disposition'],
                content_type=response.headers['Content-Type'],
                content=response.content,
            )
        )

    def _build_url(self, path: str) -> str:
        return urljoin(self._base_url, path)


def _get_user_invoiceninja_customer_id(user_id: UserID) -> str | None:
    """Fetch a user's Invoice Ninja customer ID from user details."""
    details = user_service.get_detail(user_id)
    if not details.extras:
        return None

    return details.extras.get('invoiceninja_id') or None


def _fill_client_data(user: User, order: AdminDetailedOrder) -> dict[str, Any]:
    """Fill client data."""
    mail_address = user_service.get_email_address(user.id)

    name = order.company
    if not name or name.isspace():
        name = f'{order.first_name} {order.last_name}'

    return {
        'name': name,
        'custom_value1': user.screen_name,
        'address1': order.address.street,
        'address2': '',
        'city': order.address.city,
        'state': '',
        'postal_code': order.address.postal_code,
        'contacts': [
            {
                'first_name': order.first_name,
                'last_name': order.last_name,
                'email': mail_address,
            }
        ],
    }


def _assemble_invoice_creation_request_data(
    customer_id: str, order: AdminDetailedOrder
) -> dict:
    """Assemble request data to create invoice from."""
    return {
        'client_id': customer_id,
        'po_number': order.order_number,
        'line_items': _assemble_line_items(order.line_items),
        'uses_inclusive_taxes': 1,
        'footer': _assemble_order_notes(order.id),
    }


def _assemble_line_items(line_items: list[LineItem]) -> list[dict[str, Any]]:
    """Assemble line items for Invoice Ninja."""
    return [
        {
            'notes': line_item.name,
            'cost': str(line_item.unit_price.amount),
            'quantity': line_item.quantity,
            'tax_name1': 'USt.',
            'tax_rate1': int(line_item.tax_rate * 100),
        }
        for line_item in line_items
    ]


def _assemble_order_notes(order_id: OrderID) -> str:
    """Combine order notes into single multi-line string."""
    notes = order_log_service.get_entries_of_type_for_order(
        order_id, 'order-note-added'
    )
    return '\n\n'.join(note.data['text'] for note in notes)


def _transform_invoice_response(data: dict[str, Any]) -> InvoiceNinjaInvoice:
    return InvoiceNinjaInvoice(
        id=data['id'],
        invitation_key=data['invitations'][0]['key'],
        paid_to_date=data['paid_to_date'],
        client_id=data['client_id'],
        number=data['number'],
    )
