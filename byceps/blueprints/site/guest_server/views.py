"""
byceps.blueprints.site.guest_message.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send messages from one user to another.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Iterable

from flask import abort, g, request
from flask_babel import gettext

from ....services.guest_server import service as guest_server_service
from ....services.guest_server.transfer.models import Address
from ....signals import guest_server as guest_server_signals
from ....typing import PartyID
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
    party_id = _ensure_party_or_404()

    setting = guest_server_service.get_setting_for_party(party_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
        'domain': setting.domain,
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

    flash_success(gettext('The server has been registered.'))

    guest_server_signals.guest_server_registered.send(None, event=event)

    return redirect_to('dashboard.index')


def _ensure_party_or_404() -> PartyID:
    party_id = g.party_id

    if party_id is None:
        abort(404)

    return party_id


def _sort_addresses(addresses: Iterable[Address]) -> list[Address]:
    """Sort addresses.

    By IP address first, hostname second. `None` at the end.
    """
    return list(
        sorted(
            addresses,
            key=lambda addr: (
                addr.ip_address is None,
                addr.ip_address,
                addr.hostname is None,
                addr.hostname,
            ),
        )
    )