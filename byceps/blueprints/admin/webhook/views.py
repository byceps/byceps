"""
byceps.blueprints.admin.webhook.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....services.webhooks import service as webhook_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.permission_registry import permission_registry
from ....util.framework.templating import templated
from ....util.views import permission_required

from .authorization import WebhookPermission


blueprint = create_blueprint('webhook_admin', __name__)


permission_registry.register_enum(WebhookPermission)


@blueprint.route('/')
@permission_required(WebhookPermission.view)
@templated
def index():
    """Show webhooks."""
    webhooks = webhook_service.get_all_webhooks()

    webhooks.sort(key=lambda w: (w.description is None, w.description or ''))

    return {
        'webhooks': webhooks,
    }
