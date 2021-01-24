"""
byceps.blueprints.admin.webhook.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort
from flask_babel import gettext

from ....announce.helpers import call_webhook
from ....services.webhooks import service as webhook_service
from ....util.authorization import register_permission_enum
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, respond_no_content

from .authorization import WebhookPermission


blueprint = create_blueprint('webhook_admin', __name__)


register_permission_enum(WebhookPermission)


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


@blueprint.route('/webhooks/<webhook_id>', methods=['POST'])
@permission_required(WebhookPermission.view)
@respond_no_content
def test(webhook_id):
    """Call the webhook (synchronously)."""
    webhook = webhook_service.find_webhook(webhook_id)
    if webhook is None:
        abort(404)

    text = 'Test, test … is this thing on?!'
    try:
        call_webhook(webhook, text)
        flash_success(
            gettext('Webhook call has been successful.'), icon='success'
        )
    except Exception as e:
        flash_error(
            gettext('Webhook call failed:')
            + f'<br><pre style="white-space: pre-wrap;">{e}</pre>',
            icon='warning',
            text_is_safe=True,
        )
