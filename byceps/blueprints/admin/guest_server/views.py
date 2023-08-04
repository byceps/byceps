"""
byceps.blueprints.admin.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterable
import ipaddress

from flask import abort, g, request, url_for
from flask_babel import gettext

from byceps.services.guest_server import guest_server_service
from byceps.services.guest_server.models import Address, IPAddress, Setting
from byceps.services.party import party_service
from byceps.services.user import user_service
from byceps.signals import guest_server as guest_server_signals
from byceps.util.export import serialize_tuples_to_csv
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content_with_location,
    textified,
)

from .forms import (
    AddressCreateForm,
    AddressUpdateForm,
    ServerCreateForm,
    ServerUpdateForm,
    SettingUpdateForm,
)


blueprint = create_blueprint('guest_server_admin', __name__)


# -------------------------------------------------------------------- #
# servers


@blueprint.get('/for_party/<party_id>/servers')
@permission_required('guest_server.view')
@templated
def server_index(party_id):
    """Show guest servers for a party."""
    party = _get_party_or_404(party_id)

    setting = guest_server_service.get_setting_for_party(party.id)

    servers = guest_server_service.get_all_servers_for_party(party.id)

    creator_ids = {server.creator_id for server in servers}
    owner_ids = {server.owner_id for server in servers}
    user_ids = creator_ids.union(owner_ids)
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'party': party,
        'setting': setting,
        'servers': servers,
        'users_by_id': users_by_id,
        'sort_addresses': _sort_addresses,
    }


@blueprint.get('/servers/<server_id>')
@permission_required('guest_server.view')
@templated
def server_view(server_id):
    """Show guest server."""
    server = _get_server_or_404(server_id)
    party = party_service.get_party(server.party_id)
    setting = guest_server_service.get_setting_for_party(party.id)

    user_ids = {server.creator_id, server.owner_id}
    users = user_service.get_users_for_admin(user_ids)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'party': party,
        'server': server,
        'setting': setting,
        'users_by_id': users_by_id,
        'sort_addresses': _sort_addresses,
    }


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
    netmask = _to_ip_address(form.netmask.data.strip())
    gateway = _to_ip_address(form.gateway.data.strip())

    server, event = guest_server_service.create_server(
        party,
        creator,
        owner,
        notes_admin=notes_admin,
        approved=approved,
        ip_address=ip_address,
        hostname=hostname,
        netmask=netmask,
        gateway=gateway,
    )

    flash_success(gettext('The server has been registered.'))

    guest_server_signals.guest_server_registered.send(None, event=event)

    return redirect_to('.server_view', server_id=server.id)


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

    return redirect_to('.server_view', server_id=server.id)


@blueprint.delete('/guest_servers/<uuid:server_id>')
@permission_required('guest_server.administrate')
@respond_no_content_with_location
def server_delete(server_id):
    """Delete a guest server."""
    server = _get_server_or_404(server_id)

    party_id = server.party_id

    guest_server_service.delete_server(server_id)

    flash_success(gettext('Server has been deleted.'))

    return url_for('.server_index', party_id=party_id)


# -------------------------------------------------------------------- #
# addresses


@blueprint.get('/for_party/<party_id>/addresses')
@permission_required('guest_server.view')
@templated
def address_index(party_id):
    """Show addresses for a party."""
    party = _get_party_or_404(party_id)

    servers = guest_server_service.get_all_servers_for_party(party.id)

    addresses = []
    for server in servers:
        addresses.extend(server.addresses)

    user_ids = {server.owner_id for server in servers}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)
    owners_by_server_id = {
        server.id: users_by_id[server.owner_id] for server in servers
    }

    setting = guest_server_service.get_setting_for_party(party.id)

    return {
        'party': party,
        'addresses': addresses,
        'sort_addresses': _sort_addresses,
        'owners_by_server_id': owners_by_server_id,
        'setting': setting,
    }


@blueprint.get('/for_party/<party_id>/addresses/export/netbox')
@permission_required('guest_server.view')
@textified
def address_export_netbox(party_id):
    """Export addresses for a party as NetBox-compatible CSV.

    Suitable for importing into NetBox
    (https://github.com/netbox-community/netbox).
    """
    party = _get_party_or_404(party_id)

    setting = guest_server_service.get_setting_for_party(party.id)

    all_servers = guest_server_service.get_all_servers_for_party(party.id)
    approved_servers = [server for server in all_servers if server.approved]

    owner_ids = {server.owner_id for server in approved_servers}
    owners = user_service.get_users(owner_ids, include_avatars=False)
    owners_by_id = user_service.index_users_by_id(owners)

    # field names as defined by NetBox
    field_names = ('address', 'status', 'dns_name', 'description')

    rows = []

    for server in approved_servers:
        for address in server.addresses:
            if address.ip_address and address.hostname:
                rows.append(
                    (
                        f'{str(address.ip_address)}/24',
                        'active',
                        _get_full_hostname(address.hostname, setting),
                        owners_by_id[server.owner_id].screen_name or 'unknown',
                    )
                )

    rows.sort()

    return serialize_tuples_to_csv([field_names] + rows)


def _get_full_hostname(hostname: str, setting: Setting) -> str:
    """Return the hostname with the domain (if configured) appended."""
    return hostname + '.' + setting.domain if setting.domain else hostname


@blueprint.get('/servers/<uuid:server_id>/addresses/create')
@permission_required('guest_server.administrate')
@templated
def address_create_form(server_id, erroneous_form=None):
    """Show a form to add an address to a server."""
    server = _get_server_or_404(server_id)
    party = party_service.get_party(server.party_id)

    form = erroneous_form if erroneous_form else AddressCreateForm()

    return {
        'party': party,
        'server': server,
        'form': form,
    }


@blueprint.post('/servers/<uuid:server_id>/addresses')
@permission_required('guest_server.administrate')
def address_create(server_id):
    """Add an address to a server."""
    server = _get_server_or_404(server_id)

    form = AddressCreateForm(request.form)
    if not form.validate():
        return address_create_form(server_id, form)

    ip_address = _to_ip_address(form.ip_address.data.strip())
    hostname = form.hostname.data.strip() or None
    netmask = _to_ip_address(form.netmask.data.strip())
    gateway = _to_ip_address(form.gateway.data.strip())

    guest_server_service.create_address(
        server.id, ip_address, hostname, netmask, gateway
    )

    flash_success(gettext('The address has been added.'))

    return redirect_to('.server_view', server_id=server.id)


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
    netmask = _to_ip_address(form.netmask.data.strip())
    gateway = _to_ip_address(form.gateway.data.strip())

    guest_server_service.update_address(
        address.id, ip_address, hostname, netmask, gateway
    )

    flash_success(gettext('Changes have been saved.'))

    return redirect_to('.server_view', server_id=server.id)


# -------------------------------------------------------------------- #
# setting


@blueprint.get('/for_party/<party_id>/settings')
@permission_required('guest_server.view')
@templated
def setting_view(party_id):
    """Show settings for a party."""
    party = _get_party_or_404(party_id)

    setting = guest_server_service.get_setting_for_party(party.id)

    return {
        'party': party,
        'setting': setting,
    }


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
        party, netmask, gateway, dns_server1, dns_server2, domain
    )

    flash_success(gettext('Changes have been saved.'))

    return redirect_to('.setting_view', party_id=party.id)


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


def _to_ip_address(value: str) -> IPAddress | None:
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
