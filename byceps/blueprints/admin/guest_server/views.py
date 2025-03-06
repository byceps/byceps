"""
byceps.blueprints.admin.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
import ipaddress

from flask import abort, g, request, url_for
from flask_babel import gettext

from byceps.services.guest_server import (
    guest_server_domain_service,
    guest_server_export_service,
    guest_server_service,
    signals as guest_server_signals,
)
from byceps.services.guest_server.models import (
    Address,
    AddressData,
    IPAddress,
    ServerStatus,
)
from byceps.services.party import party_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
    respond_no_content_with_location,
    textified,
)

from .forms import (
    AddressCreateForm,
    AddressUpdateForm,
    ServerRegisterForm,
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

    only_status_str = request.args.get('only_status')
    only_status = ServerStatus.__members__.get(only_status_str)

    servers = guest_server_service.get_all_servers_for_party(party.id)

    # Do this before filtering!
    server_quantities_by_status = (
        guest_server_domain_service.get_server_quantities_by_status(servers)
    )

    if only_status:
        servers = guest_server_domain_service.filter_servers_by_status(
            servers, only_status
        )
    servers.sort(key=lambda server: server.created_at, reverse=True)
    servers.sort(key=_get_sort_value_for_server_status)

    return {
        'party': party,
        'setting': setting,
        'only_status': only_status,
        'server_quantities_by_status': server_quantities_by_status,
        'servers': servers,
        'sort_addresses': _sort_addresses,
    }


def _get_sort_value_for_server_status(server):
    if server.checked_out:
        return 4
    elif server.checked_in:
        return 3
    elif server.approved:
        return 2
    else:
        return 1


@blueprint.get('/servers/<server_id>')
@permission_required('guest_server.view')
@templated
def server_view(server_id):
    """Show guest server."""
    server = _get_server_or_404(server_id)
    party = party_service.get_party(server.party_id)
    setting = guest_server_service.get_setting_for_party(party.id)

    owner_ids = {server.creator.id, server.owner.id}
    owners_by_id = user_service.get_users_for_admin_indexed_by_id(owner_ids)

    return {
        'party': party,
        'server': server,
        'setting': setting,
        'owners_by_id': owners_by_id,
        'sort_addresses': _sort_addresses,
    }


@blueprint.get('/for_party/<party_id>/servers/create')
@permission_required('guest_server.administrate')
@templated
def server_create_form(party_id, erroneous_form=None):
    """Show a form to register a guest server."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else ServerRegisterForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>/servers')
@permission_required('guest_server.administrate')
def server_create(party_id):
    """Register a guest server."""
    party = _get_party_or_404(party_id)

    form = ServerRegisterForm(request.form)
    if not form.validate():
        return server_create_form(party_id, form)

    creator = g.user
    owner = form.owner.data
    description = form.description.data.strip()
    address_datas = {
        AddressData(
            ip_address=_to_ip_address(form.ip_address.data.strip()),
            hostname=form.hostname.data.strip().lower(),
            netmask=_to_ip_address(form.netmask.data.strip()),
            gateway=_to_ip_address(form.gateway.data.strip()),
        ),
    }
    notes_admin = form.notes_admin.data.strip()

    server, event = guest_server_service.register_server(
        party,
        creator,
        owner,
        description,
        address_datas,
        notes_admin=notes_admin,
    )

    flash_success(gettext('The server has been registered.'))

    guest_server_signals.guest_server_registered.send(None, event=event)

    return redirect_to('.server_view', server_id=server.id)


@blueprint.get('/servers/<uuid:server_id>/update')
@permission_required('guest_server.administrate')
@templated
def server_update_form(server_id, erroneous_form=None):
    """Show form to update a guest server."""
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
    """Update a guest server."""
    server = _get_server_or_404(server_id)

    form = ServerUpdateForm(request.form)
    if not form.validate():
        return server_update_form(server.id, form)

    notes_admin = form.notes_admin.data.strip() or None

    guest_server_service.update_server(server.id, notes_admin)

    flash_success(gettext('Changes have been saved.'))

    return redirect_to('.server_view', server_id=server.id)


@blueprint.post('/guest_servers/<uuid:server_id>/approve')
@permission_required('guest_server.administrate')
@respond_no_content
def server_approve(server_id):
    """Approve a guest server."""
    server = _get_server_or_404(server_id)
    initiator = g.user

    result = guest_server_service.approve_server(server, initiator)
    if result.is_err():
        flash_error(result.unwrap_err())
        return

    flash_success(gettext('Server has been approved.'))

    _, event = result.unwrap()

    guest_server_signals.guest_server_approved.send(None, event=event)


@blueprint.post('/guest_servers/<uuid:server_id>/checkin')
@permission_required('guest_server.administrate')
@respond_no_content
def server_check_in(server_id):
    """Check in a guest server."""
    server = _get_server_or_404(server_id)
    initiator = g.user

    result = guest_server_service.check_in_server(server, initiator)
    if result.is_err():
        flash_error(result.unwrap_err())
        return

    flash_success(gettext('Server has been checked in.'))

    _, event = result.unwrap()

    guest_server_signals.guest_server_checked_in.send(None, event=event)


@blueprint.post('/guest_servers/<uuid:server_id>/checkout')
@permission_required('guest_server.administrate')
@respond_no_content
def server_check_out(server_id):
    """Check out a guest server."""
    server = _get_server_or_404(server_id)
    initiator = g.user

    result = guest_server_service.check_out_server(server, initiator)
    if result.is_err():
        flash_error(result.unwrap_err())
        return

    flash_success(gettext('Server has been checked out.'))

    _, event = result.unwrap()

    guest_server_signals.guest_server_checked_out.send(None, event=event)


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

    owner_ids = {server.owner.id for server in servers}
    owners_by_id = user_service.get_users_indexed_by_id(
        owner_ids, include_avatars=True
    )
    owners_by_server_id = {
        server.id: owners_by_id[server.owner.id] for server in servers
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

    servers = guest_server_service.get_all_servers_for_party(party.id)
    setting = guest_server_service.get_setting_for_party(party.id)

    return guest_server_export_service.export_addresses_for_netbox(
        servers, setting
    )


@blueprint.get('/servers/<uuid:server_id>/addresses/create')
@permission_required('guest_server.administrate')
@templated
def address_create_form(server_id, erroneous_form=None):
    """Show a form to add an address to a guest server."""
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
    """Add an address to a guest server."""
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

    update_result = guest_server_service.update_address(
        address.id, ip_address, hostname, netmask, gateway
    )

    if update_result.is_err():
        flash_error(update_result.unwrap_err())
    else:
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

    By IP address first, hostname second. `None` at the beginning.
    """
    return list(
        sorted(
            addresses,
            key=lambda addr: (
                addr.ip_address is not None,
                addr.ip_address,
                addr.hostname is not None,
                addr.hostname,
            ),
        )
    )
