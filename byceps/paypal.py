"""
byceps.paypal
~~~~~~~~~~~~~

PayPal integration

:Copyright: 2020 Jan Korneffel
:License: Revised BSD (see `LICENSE` file for details)
"""

from paypalcheckoutsdk.core import (
    LiveEnvironment,
    PayPalHttpClient,
    SandboxEnvironment,
)

from byceps.config.errors import ConfigurationError


class PayPalClient:
    def init_app(self, app):
        """Prepare PayPal HTTP client instance with environment that has
        access credentials context.

        Use this instance to invoke PayPal APIs, provided the
        credentials have access.
        """
        self.client_id = app.config.get('PAYPAL_CLIENT_ID')
        self.client_secret = app.config.get('PAYPAL_CLIENT_SECRET')

        if self.client_id is not None and self.client_secret is None:
            raise ConfigurationError(
                'PayPal is enabled, but PAYPAL_CLIENT_SECRET is missing.'
            )

        if app.config.get('PAYPAL_ENVIRONMENT', 'sandbox') == 'live':
            self.environment = LiveEnvironment(
                client_id=self.client_id, client_secret=self.client_secret
            )
        else:
            self.environment = SandboxEnvironment(
                client_id=self.client_id, client_secret=self.client_secret
            )

        self.client = PayPalHttpClient(self.environment)


paypal = PayPalClient()
