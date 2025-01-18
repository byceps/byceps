"""
application instance
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.application import create_cli_app
from byceps.config.integration import (
    read_configuration_from_file_given_in_env_var,
)
from byceps.services.shop.order import order_service
from byceps.services.shop.order.models.order import (
    PaymentState as OrderPaymentState,
)
from byceps.services.ticketing.ticket_service import find_ticket_by_code
from byceps.services.user import user_service


_, config_overrides = read_configuration_from_file_given_in_env_var()
app = create_cli_app(config_overrides=config_overrides)


@app.shell_context_processor
def extend_shell_context():
    """Provide common objects to make available in the application shell."""
    return {
        'app': app,
        'find_order_by_order_number': order_service.find_order_by_order_number,
        'OrderPaymentState': OrderPaymentState,
        'find_ticket_by_code': find_ticket_by_code,
        'find_db_user_by_screen_name': user_service.find_db_user_by_screen_name,
        'find_user_by_screen_name': user_service.find_user_by_screen_name,
    }
