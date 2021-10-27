"""
byceps.blueprints.site.guest_message.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send messages from one user to another.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from ....services.guest_server import service as guest_server_service
from ....signals import guest_server as guest_server_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import login_required, redirect_to

from .forms import CreateForm


blueprint = create_blueprint('guest_server', __name__)


@blueprint.get('/create')
@login_required
@templated
def create_form(erroneous_form=None):
    """Show a form to create a guest server."""
    _ensure_party_or_404()

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.post('/create')
@login_required
def create():
    """Create a guest server."""
    _ensure_party_or_404()

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(form)

    hostname = form.hostname.data.strip().lower()
    notes = form.notes.data.strip()

    server, event = guest_server_service.create_server(
        g.party_id, g.user.id, g.user.id, notes_owner=notes, hostname=hostname
    )

    flash_success(gettext('Your server has been registered.'))

    guest_server_signals.guest_server_registered.send(None, event=event)

    return redirect_to('dashboard.index')


def _ensure_party_or_404():
    if g.party_id is None:
        abort(404)
