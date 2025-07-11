"""
byceps.services.shop.invoice.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class InvoiceError:
    """Base class for errors related to the integration of an invoice
    provider.
    """


@dataclass(frozen=True)
class InvoiceDeniedForFreeOrderError(InvoiceError):
    """Invoices should not be created for orders paid as "free"."""


@dataclass(frozen=True)
class InvoiceDownloadError(InvoiceError):
    """Invoice document could not be downloaded from invoice provider."""


@dataclass(frozen=True)
class InvoiceProviderConfigurationError(InvoiceError):
    """The integration of an invoice provider is not configured
    correctly.
    """


@dataclass(frozen=True)
class InvoiceProviderNotEnabledError(InvoiceError):
    """Invoice provider is not enabled."""
