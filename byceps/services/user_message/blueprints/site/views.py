"""
byceps.services.user_message.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send messages from one user to another.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request, url_for
from flask_babel import gettext

from byceps.services.user import user_service
from byceps.services.user_message import user_message_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import login_required, redirect_to

from .forms import CreateForm


blueprint = create_blueprint('user_message', __name__)


@blueprint.get('/to/<uuid:recipient_id>')
@login_required
@templated
def create_form(recipient_id, erroneous_form=None):
    """Show a form to send a message to the user."""
    recipient = _get_user_or_404(recipient_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'recipient': recipient,
        'form': form,
    }


@blueprint.post('/to/<uuid:recipient_id>')
@login_required
def create(recipient_id):
    """Send a message to the user."""
    recipient = _get_user_or_404(recipient_id)

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(recipient.id, form)

    sender = g.user
    body = form.body.data.strip()
    sender_contact_url = url_for(
        '.create_form', recipient_id=sender.id, _external=True
    )

    user_message_service.send_message(
        sender.id, recipient.id, body, sender_contact_url, g.site_id
    )

    flash_success(
        gettext(
            'Your message to %(screen_name)s has been sent.',
            screen_name=recipient.screen_name,
        )
    )

    return redirect_to('user_profile.view', user_id=recipient.id)


def _get_user_or_404(user_id):
    user = user_service.find_active_user(user_id, include_avatar=True)

    if user is None:
        abort(404)

    return user
