"""
byceps.blueprints.site.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from flask import abort, g, redirect, request
from flask_babel import gettext

from byceps.services.global_setting import global_setting_service
from byceps.services.guest_server import (
    guest_server_domain_service,
    guest_server_service,
)
from byceps.services.guest_server.models import Address
from byceps.services.party.models import Party
from byceps.services.ticketing import ticket_service
from byceps.signals import guest_server as guest_server_signals
from byceps.typing import PartyID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import login_required, permission_required, redirect_to

from .forms import CreateForm


blueprint = create_blueprint('guest_server', __name__)


@blueprint.get('')
@login_required
@templated
def index():
    """List current user's guest servers."""
    party = _get_current_party_or_404()

    servers = guest_server_service.get_servers_for_owner_and_party(
        g.user.id, party.id
    )

    setting = guest_server_service.get_setting_for_party(party.id)

    return {
        'servers': servers,
        'setting': setting,
        'sort_addresses': _sort_addresses,
    }


@blueprint.get('/create')
@login_required
@templated
def create_form(erroneous_form=None):
    """Show a form to create a guest server."""
    party = _get_current_party_or_404()

    if not _current_user_uses_ticket_for_party(party.id):
        flash_success(gettext('Using a ticket for this party is required.'))
        return redirect_to('.index')

    if _server_limit_reached(party.id):
        flash_success(
            gettext(
                'You have already registered the maximum number of servers allowed.'
            )
        )
        return redirect_to('.index')

    setting = guest_server_service.get_setting_for_party(party.id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
        'domain': setting.domain,
    }


@blueprint.post('/create')
@login_required
def create():
    """Create a guest server."""
    party = _get_current_party_or_404()

    if not _current_user_uses_ticket_for_party(party.id):
        flash_success(gettext('Using a ticket for this party is required.'))
        return redirect_to('.index')

    if _server_limit_reached(party.id):
        flash_success(
            gettext(
                'You have already registered the maximum number of servers allowed.'
            )
        )
        return redirect_to('.index')

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(form)

    hostname = form.hostname.data.strip().lower()
    notes = form.notes.data.strip()

    server, event = guest_server_service.create_server(
        party, g.user, g.user, notes_owner=notes, hostname=hostname
    )

    flash_success(gettext('The server has been registered.'))

    guest_server_signals.guest_server_registered.send(None, event=event)

    return redirect_to('.index')


@blueprint.get('/servers/<server_id>/admin')
@permission_required('guest_server.administrate')
def server_view(server_id):
    """Show guest server."""
    server = guest_server_service.find_server(server_id)
    if server is None:
        abort(404)

    admin_url_root = global_setting_service.find_setting_value('admin_url_root')
    if not admin_url_root:
        abort(500, 'Admin URL root not configured.')

    url = f'https://{admin_url_root}/admin/guest_servers/servers/{server.id}'
    return redirect(url)


def _get_current_party_or_404() -> Party:
    party = g.party

    if party is None:
        abort(404)

    return party


def _current_user_uses_ticket_for_party(party_id: PartyID) -> bool:
    return ticket_service.uses_any_ticket_for_party(g.user.id, party_id)


def _server_limit_reached(party_id: PartyID) -> bool:
    quantity = guest_server_service.count_servers_for_owner_and_party(
        g.user.id, party_id
    )

    return guest_server_domain_service.is_server_quantity_limit_reached(
        quantity
    )


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
