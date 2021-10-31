"""
byceps.blueprints.admin.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import ipaddress
from typing import Iterable, Optional

from flask import abort, g, request
from flask_babel import gettext

from ....services.guest_server import service as guest_server_service
from ....services.guest_server.transfer.models import Address, IPAddress
from ....services.party import service as party_service
from ....services.user import service as user_service
from ....signals import guest_server as guest_server_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to, respond_no_content

from .forms import (
    AddressUpdateForm,
    ServerCreateForm,
    ServerUpdateForm,
    SettingUpdateForm,
)


blueprint = create_blueprint('guest_server_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('guest_server.view')
@templated
def index(party_id):
    """Show guest servers for a party."""
    party = _get_party_or_404(party_id)

    setting = guest_server_service.get_setting_for_party(party.id)

    servers = guest_server_service.get_all_servers_for_party(party.id)

    creator_ids = {server.creator_id for server in servers}
    owner_ids = {server.owner_id for server in servers}
    user_ids = creator_ids.union(owner_ids)
    users = user_service.get_users_for_admin(user_ids)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'party': party,
        'setting': setting,
        'servers': servers,
        'users_by_id': users_by_id,
        'sort_addresses': _sort_addresses,
    }


# -------------------------------------------------------------------- #
# setting


@blueprint.get('/for_party/<party_id>/settings/update')
@permission_required('guest_server.administrate')
@templated
def setting_update_form(party_id, erroneous_form=None):
    """Show form to update the settings for a party."""
    party = _get_party_or_404(party_id)

    setting = guest_server_service.get_setting_for_party(party.id)

    form = erroneous_form if erroneous_form else SettingUpdateForm(obj=setting)

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>/settings')
@permission_required('guest_server.administrate')
def setting_update(party_id):
    """Update the settings for a party."""
    party = _get_party_or_404(party_id)

    form = SettingUpdateForm(request.form)
    if not form.validate():
        return setting_update_form(party.id, form)

    netmask = _to_ip_address(form.netmask.data.strip())
    gateway = _to_ip_address(form.gateway.data.strip())
    dns_server1 = _to_ip_address(form.dns_server1.data.strip())
    dns_server2 = _to_ip_address(form.dns_server2.data.strip())
    domain = form.domain.data.strip() or None

    guest_server_service.update_setting(
        party.id, netmask, gateway, dns_server1, dns_server2, domain
    )

    flash_success(gettext('Changes have been saved.'))

    return redirect_to('.index', party_id=party.id)


# -------------------------------------------------------------------- #
# servers


@blueprint.get('/for_party/<party_id>/servers/create')
@permission_required('guest_server.administrate')
@templated
def server_create_form(party_id, erroneous_form=None):
    """Show a form to create a server."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else ServerCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>/servers')
@permission_required('guest_server.administrate')
def server_create(party_id):
    """Create a server."""
    party = _get_party_or_404(party_id)

    form = ServerCreateForm(request.form)
    if not form.validate():
        return server_create_form(party_id, form)

    creator = g.user
    owner = form.owner.data
    notes_admin = form.notes_admin.data.strip()
    approved = form.approved.data
    ip_address = _to_ip_address(form.ip_address.data.strip())
    hostname = form.hostname.data.strip() or None

    server, event = guest_server_service.create_server(
        party.id,
        creator.id,
        owner.id,
        notes_admin=notes_admin,
        approved=approved,
        ip_address=ip_address,
        hostname=hostname,
    )

    flash_success(gettext('The server has been registered.'))

    guest_server_signals.guest_server_registered.send(None, event=event)

    return redirect_to('.index', party_id=party.id)


@blueprint.get('/servers/<uuid:server_id>/update')
@permission_required('guest_server.administrate')
@templated
def server_update_form(server_id, erroneous_form=None):
    """Show form to update a server."""
    server = _get_server_or_404(server_id)
    party = party_service.get_party(server.party_id)

    form = erroneous_form if erroneous_form else ServerUpdateForm(obj=server)

    return {
        'party': party,
        'server': server,
        'form': form,
    }


@blueprint.post('/servers/<uuid:server_id>')
@permission_required('guest_server.administrate')
def server_update(server_id):
    """Update a server."""
    server = _get_server_or_404(server_id)

    form = ServerUpdateForm(request.form)
    if not form.validate():
        return server_update_form(server.id, form)

    notes_admin = form.notes_admin.data.strip() or None
    approved = form.approved.data

    guest_server_service.update_server(server.id, notes_admin, approved)

    flash_success(gettext('Changes have been saved.'))

    return redirect_to('.index', party_id=server.party_id)


@blueprint.delete('/guest_servers/<uuid:server_id>')
@permission_required('guest_server.administrate')
@respond_no_content
def delete_server(server_id):
    """Delete a guest server."""
    guest_server_service.delete_server(server_id)

    flash_success(gettext('Server has been deleted.'))


# -------------------------------------------------------------------- #
# address


@blueprint.get('/addresses/<uuid:address_id>/update')
@permission_required('guest_server.administrate')
@templated
def address_update_form(address_id, erroneous_form=None):
    """Show form to update an address."""
    address = _get_address_or_404(address_id)
    server = guest_server_service.find_server(address.server_id)
    party = party_service.get_party(server.party_id)

    form = erroneous_form if erroneous_form else AddressUpdateForm(obj=address)

    return {
        'party': party,
        'address': address,
        'form': form,
    }


@blueprint.post('/addresses/<uuid:address_id>')
@permission_required('guest_server.administrate')
def address_update(address_id):
    """Update an address."""
    address = _get_address_or_404(address_id)
    server = guest_server_service.find_server(address.server_id)

    form = AddressUpdateForm(request.form)
    if not form.validate():
        return address_update_form(address.id, form)

    ip_address = _to_ip_address(form.ip_address.data.strip())
    hostname = form.hostname.data.strip() or None

    guest_server_service.update_address(address.id, ip_address, hostname)

    flash_success(gettext('Changes have been saved.'))

    return redirect_to('.index', party_id=server.party_id)


# -------------------------------------------------------------------- #
# helpers


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_server_or_404(server_id):
    server = guest_server_service.find_server(server_id)

    if server is None:
        abort(404)

    return server


def _get_address_or_404(address_id):
    address = guest_server_service.find_address(address_id)

    if address is None:
        abort(404)

    return address


def _to_ip_address(value: str) -> Optional[IPAddress]:
    return ipaddress.ip_address(value) if value else None


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