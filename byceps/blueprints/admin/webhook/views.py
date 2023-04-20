"""
byceps.blueprints.admin.webhook.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
import json

from flask import abort, request
from flask_babel import gettext

from byceps.announce.helpers import assemble_request_data, call_webhook
from byceps.services.webhooks import webhook_service
from byceps.services.webhooks.models import OutgoingWebhook, WebhookID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('webhook_admin', __name__)


@blueprint.get('/')
@permission_required('webhook.view')
@templated
def index():
    """Show webhooks."""
    webhooks = webhook_service.get_all_webhooks()

    webhooks.sort(key=lambda w: (w.description is None, w.description or ''))

    return {
        'webhooks': webhooks,
    }


@blueprint.get('/create')
@permission_required('webhook.administrate')
@templated
def create_form(erroneous_form=None):
    """Show form to create a webhook."""
    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.post('/')
@permission_required('webhook.administrate')
def create():
    """Create a webhook."""
    form = CreateForm(request.form)

    if not form.validate():
        return create_form(form)

    event_types = set(form.event_types.data)
    event_filters = {}
    format = form.format.data.strip()
    url = form.url.data.strip()
    description = form.description.data.strip()
    enabled = False

    webhook_service.create_outgoing_webhook(
        event_types,
        event_filters,
        format,
        url,
        enabled,
        description=description,
    )

    flash_success(gettext('Webhook has been created.'))

    return redirect_to('.index')


@blueprint.get('/webhooks/<uuid:webhook_id>/update')
@permission_required('webhook.administrate')
@templated
def update_form(webhook_id, erroneous_form=None):
    """Show form to update a webhook."""
    webhook = _get_webhook_or_404(webhook_id)

    if erroneous_form:
        form = erroneous_form
    else:
        data = dataclasses.asdict(webhook)
        data['extra_fields'] = json.dumps(webhook.extra_fields)
        form = UpdateForm(data=data)

    return {
        'webhook': webhook,
        'form': form,
    }


@blueprint.post('/webhooks/<uuid:webhook_id>')
@permission_required('webhook.administrate')
def update(webhook_id):
    """Update the webhook."""
    webhook = _get_webhook_or_404(webhook_id)

    form = UpdateForm(request.form)

    if not form.validate():
        return update_form(webhook.id, form)

    event_types = set(form.event_types.data)
    # Event filters cannot be edited at the moment,
    # but at least don't remove them on update.
    event_filters = webhook.event_filters
    format = form.format.data.strip()
    url = form.url.data.strip()
    text_prefix = form.text_prefix.data.lstrip()  # Allow trailing whitespace.
    extra_fields_str = form.extra_fields.data.strip()
    extra_fields = json.loads(extra_fields_str) if extra_fields_str else None
    description = form.description.data.strip()
    enabled = form.enabled.data

    webhook = webhook_service.update_outgoing_webhook(
        webhook.id,
        event_types,
        event_filters,
        format,
        text_prefix,
        extra_fields,
        url,
        description,
        enabled,
    ).unwrap()

    flash_success(gettext('Webhook has been updated.'))

    return redirect_to('.index')


@blueprint.delete('/webhooks/<uuid:webhook_id>/test')
@permission_required('webhook.administrate')
@respond_no_content
def delete(webhook_id):
    """Remove the webhook."""
    webhook = _get_webhook_or_404(webhook_id)

    webhook_service.delete_outgoing_webhook(webhook.id)

    flash_success(gettext('Webhook has been removed.'))


@blueprint.post('/webhooks/<uuid:webhook_id>/test')
@permission_required('webhook.administrate')
@respond_no_content
def test(webhook_id):
    """Call the webhook (synchronously)."""
    webhook = _get_webhook_or_404(webhook_id)

    text = 'Test, test … is this thing on?!'
    try:
        request_data = assemble_request_data(webhook, text)
        call_webhook(webhook, request_data)

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


# helpers


def _get_webhook_or_404(webhook_id: WebhookID) -> OutgoingWebhook:
    webhook = webhook_service.find_webhook(webhook_id)

    if webhook is None:
        abort(404)

    return webhook
