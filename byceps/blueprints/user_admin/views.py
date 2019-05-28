"""
byceps.blueprints.user_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict
from operator import attrgetter

from flask import abort, g, redirect, request, url_for

from ...services.authentication.password import service as password_service
from ...services.authorization import service as authorization_service
from ...services.orga_team import service as orga_team_service
from ...services.party import service as party_service
from ...services.shop.order import service as order_service
from ...services.shop.shop import service as shop_service
from ...services.ticketing import attendance_service, ticket_service
from ...services.user import command_service as user_command_service
from ...services.user import creation_service as user_creation_service
from ...services.user import service as user_service
from ...services.user import stats_service as user_stats_service
from ...services.user_badge import service as badge_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import redirect_to, respond_no_content

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..authorization_admin.authorization import RolePermission
from ..user.signals import account_created, account_deleted, \
    account_suspended, account_unsuspended

from .authorization import UserPermission
from .forms import CreateAccountForm, DeleteAccountForm, SetPasswordForm, \
    SuspendAccountForm
from .models import UserStateFilter
from . import service


blueprint = create_blueprint('user_admin', __name__)


permission_registry.register_enum(UserPermission)


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@permission_required(UserPermission.view)
@templated
def index(page):
    """List users."""
    per_page = request.args.get('per_page', type=int, default=20)
    search_term = request.args.get('search_term', default='').strip()
    only = request.args.get('only')

    user_state_filter = UserStateFilter.__members__.get(only,
                                                        UserStateFilter.none)

    users = service.get_users_paginated(page, per_page,
                                        search_term=search_term,
                                        state_filter=user_state_filter)

    total_enabled = user_stats_service.count_enabled_users()
    total_disabled = user_stats_service.count_disabled_users()
    total_suspended = user_stats_service.count_suspended_users()
    total_deleted = user_stats_service.count_deleted_users()
    total_overall = total_enabled + total_disabled

    return {
        'users': users,
        'total_enabled': total_enabled,
        'total_disabled': total_disabled,
        'total_suspended': total_suspended,
        'total_deleted': total_deleted,
        'total_overall': total_overall,
        'search_term': search_term,
        'only': only,
        'UserStateFilter': UserStateFilter,
        'user_state_filter': user_state_filter,
    }


@blueprint.route('/<uuid:user_id>')
@permission_required(UserPermission.view)
@templated
def view(user_id):
    """Show a user's interal profile."""
    user = user_service.find_user_with_details(user_id)
    if user is None:
        abort(404)

    orga_team_memberships = orga_team_service.get_memberships_for_user(user.id)

    badges_with_awarding_quantity = badge_service.get_badges_for_user(user.id)

    orders = order_service.get_orders_placed_by_user(user.id)
    order_shop_ids = {order.shop_id for order in orders}
    order_parties_by_shop_id = _get_parties_by_shop_id(order_shop_ids)

    parties_and_tickets = _get_parties_and_tickets(user.id)

    attended_parties = attendance_service.get_attended_parties(user.id)
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)

    return {
        'user': user,
        'orga_team_memberships': orga_team_memberships,
        'badges_with_awarding_quantity': badges_with_awarding_quantity,
        'orders': orders,
        'order_parties_by_shop_id': order_parties_by_shop_id,
        'parties_and_tickets': parties_and_tickets,
        'attended_parties': attended_parties,
    }


def _get_parties_and_tickets(user_id):
    tickets = ticket_service.find_tickets_related_to_user(user_id)

    tickets_by_party_id = _group_tickets_by_party_id(tickets)

    party_ids = tickets_by_party_id.keys()
    parties_by_id = _get_parties_by_id(party_ids)

    parties_and_tickets = [
        (parties_by_id[party_id], tickets)
        for party_id, tickets in tickets_by_party_id.items()]

    parties_and_tickets.sort(key=lambda x: x[0].starts_at, reverse=True)

    return parties_and_tickets


def _group_tickets_by_party_id(tickets):
    tickets_by_party_id = defaultdict(list)

    for ticket in tickets:
        tickets_by_party_id[ticket.category.party_id].append(ticket)

    return tickets_by_party_id


def _get_parties_by_id(party_ids):
    parties = party_service.get_parties(party_ids)
    return {p.id: p for p in parties}


def _get_parties_by_shop_id(shop_ids):
    shops = shop_service.find_shops(shop_ids)
    party_ids = {shop.party_id for shop in shops}

    parties = party_service.get_parties(party_ids)
    parties_by_id = {p.id: p for p in parties}

    parties_by_shop_id = {}
    for shop in shops:
        party = parties_by_id[shop.party_id]
        parties_by_shop_id[shop.id] = party

    return parties_by_shop_id


@blueprint.route('/create')
@permission_required(UserPermission.create)
@templated
def create_account_form(erroneous_form=None):
    """Show a form to create a user account."""
    form = erroneous_form if erroneous_form else CreateAccountForm()

    return {'form': form}


@blueprint.route('/', methods=['POST'])
@permission_required(UserPermission.create)
def create_account():
    """Create a user account."""
    form = CreateAccountForm(request.form)

    if not form.validate():
        return create_account_form(form)

    screen_name = form.screen_name.data.strip()
    first_names = form.first_names.data.strip()
    last_name = form.last_name.data.strip()
    email_address = form.email_address.data.lower()
    password = form.password.data

    if user_service.is_screen_name_already_assigned(screen_name):
        flash_error(
            'Dieser Benutzername ist bereits einem Benutzerkonto zugeordnet.')
        return create_account_form(form)

    if user_service.is_email_address_already_assigned(email_address):
        flash_error(
            'Diese E-Mail-Adresse ist bereits einem Benutzerkonto zugeordnet.')
        return create_account_form(form)

    try:
        user = user_creation_service.create_basic_user(
            screen_name, email_address, password, first_names=first_names,
            last_name=last_name, creator_id=g.current_user.id)
    except user_creation_service.UserCreationFailed:
        flash_error('Das Benutzerkonto für "{}" konnte nicht angelegt werden.',
                    screen_name)
        return create_account_form(form)

    flash_success('Das Benutzerkonto "{}" wurde angelegt.', user.screen_name)
    account_created.send(None, user_id=user.id)

    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/password')
@permission_required(UserPermission.set_password)
@templated
def set_password_form(user_id, erroneous_form=None):
    """Show a form to set a new password for the user."""
    user = _get_user_or_404(user_id)

    form = erroneous_form if erroneous_form else SetPasswordForm()

    return {
        'user': user,
        'form': form,
    }


@blueprint.route('/<uuid:user_id>/password', methods=['POST'])
@permission_required(UserPermission.set_password)
def set_password(user_id):
    """Set a new password for the user."""
    user = _get_user_or_404(user_id)

    form = SetPasswordForm(request.form)
    if not form.validate():
        return set_password_form(user.id, form)

    new_password = form.password.data
    initiator_id = g.current_user.id

    password_service.update_password_hash(user.id, new_password, initiator_id)

    flash_success("Für Benutzerkonto '{}' wurde ein neues Passwort gesetzt.",
                  user.screen_name)

    return redirect(url_for('.view', user_id=user.id))


@blueprint.route('/<uuid:user_id>/flags/enabled', methods=['POST'])
@permission_required(UserPermission.administrate)
@respond_no_content
def set_enabled_flag(user_id):
    """Enable the user."""
    user = _get_user_or_404(user_id)

    initiator_id = g.current_user.id

    user_command_service.enable_user(user.id, initiator_id)

    flash_success("Das Benutzerkonto '{}' wurde aktiviert.", user.screen_name)


@blueprint.route('/<uuid:user_id>/flags/enabled', methods=['DELETE'])
@permission_required(UserPermission.administrate)
@respond_no_content
def unset_enabled_flag(user_id):
    """Disable the user."""
    user = _get_user_or_404(user_id)

    initiator_id = g.current_user.id

    user_command_service.disable_user(user.id, initiator_id)

    flash_success("Das Benutzerkonto '{}' wurde deaktiviert.", user.screen_name)


@blueprint.route('/<uuid:user_id>/suspend')
@permission_required(UserPermission.administrate)
@templated
def suspend_account_form(user_id, erroneous_form=None):
    """Show form to suspend the user account."""
    user = _get_user_or_404(user_id)

    if user.suspended:
        flash_error("Das Benutzerkonto '{}' ist bereits gesperrt.",
                    user.screen_name)
        return redirect_to('.view', user_id=user.id)

    form = erroneous_form if erroneous_form else SuspendAccountForm()

    return {
        'user': user,
        'form': form,
    }


@blueprint.route('/<uuid:user_id>/suspend', methods=['POST'])
@permission_required(UserPermission.administrate)
def suspend_account(user_id):
    """Suspend the user account."""
    user = _get_user_or_404(user_id)

    if user.suspended:
        flash_error("Das Benutzerkonto '{}' ist bereits gesperrt.",
                    user.screen_name)
        return redirect_to('.view', user_id=user.id)

    form = SuspendAccountForm(request.form)
    if not form.validate():
        return suspend_account_form(user.id, form)

    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    user_command_service.suspend_account(user.id, initiator_id, reason)

    account_suspended.send(None, user_id=user.id, initiator_id=initiator_id)

    flash_success("Das Benutzerkonto '{}' wurde gesperrt.", user.screen_name)
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/unsuspend')
@permission_required(UserPermission.administrate)
@templated
def unsuspend_account_form(user_id, erroneous_form=None):
    """Show form to unsuspend the user account."""
    user = _get_user_or_404(user_id)

    if not user.suspended:
        flash_error("Das Benutzerkonto '{}' ist bereits entsperrt.",
                    user.screen_name)
        return redirect_to('.view', user_id=user.id)

    form = erroneous_form if erroneous_form else SuspendAccountForm()

    return {
        'user': user,
        'form': form,
    }


@blueprint.route('/<uuid:user_id>/unsuspend', methods=['POST'])
@permission_required(UserPermission.administrate)
def unsuspend_account(user_id):
    """Unsuspend the user account."""
    user = _get_user_or_404(user_id)

    if not user.suspended:
        flash_error("Das Benutzerkonto '{}' ist bereits entsperrt.",
                    user.screen_name)
        return redirect_to('.view', user_id=user.id)

    form = SuspendAccountForm(request.form)
    if not form.validate():
        return unsuspend_account_form(user.id, form)

    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    user_command_service.unsuspend_account(user.id, initiator_id, reason)

    account_unsuspended.send(None, user_id=user.id, initiator_id=initiator_id)

    flash_success("Das Benutzerkonto '{}' wurde entsperrt.", user.screen_name)
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/delete')
@permission_required(UserPermission.administrate)
@templated
def delete_account_form(user_id, erroneous_form=None):
    """Show form to delete the user account."""
    user = _get_user_or_404(user_id)

    if user.deleted:
        flash_error("Das Benutzerkonto '{}' ist bereits gelöscht worden.",
                    user.screen_name)
        return redirect_to('.view', user_id=user.id)

    form = erroneous_form if erroneous_form else DeleteAccountForm()

    return {
        'user': user,
        'form': form,
    }


@blueprint.route('/<uuid:user_id>/delete', methods=['POST'])
@permission_required(UserPermission.administrate)
def delete_account(user_id):
    """Delete the user account."""
    user = _get_user_or_404(user_id)

    if user.deleted:
        flash_error("Das Benutzerkonto '{}' ist bereits gelöscht worden.",
                    user.screen_name)
        return redirect_to('.view', user_id=user.id)

    form = DeleteAccountForm(request.form)
    if not form.validate():
        return delete_account_form(user.id, form)

    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    user_command_service.delete_account(user.id, initiator_id, reason)

    account_deleted.send(None, user_id=user.id, initiator_id=initiator_id)

    flash_success("Das Benutzerkonto '{}' wurde gelöscht.", user.screen_name)
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/permissions')
@permission_required(UserPermission.view)
@templated
def view_permissions(user_id):
    """Show user's permissions."""
    user = _get_user_or_404(user_id)

    permissions_by_role = authorization_service \
        .get_permissions_by_roles_for_user_with_titles(user.id)

    return {
        'user': user,
        'permissions_by_role': permissions_by_role,
    }


@blueprint.route('/<uuid:user_id>/roles/assignment')
@permission_required(RolePermission.assign)
@templated
def manage_roles(user_id):
    """Manage what roles are assigned to the user."""
    user = _get_user_or_404(user_id)

    permissions_by_role = authorization_service \
        .get_permissions_by_roles_with_titles()

    user_role_ids = authorization_service.find_role_ids_for_user(user.id)

    return {
        'user': user,
        'permissions_by_role': permissions_by_role,
        'user_role_ids': user_role_ids,
    }


@blueprint.route('/<uuid:user_id>/roles/<role_id>', methods=['POST'])
@permission_required(RolePermission.assign)
@respond_no_content
def role_assign(user_id, role_id):
    """Assign the role to the user."""
    user = _get_user_or_404(user_id)
    role = _get_role_or_404(role_id)
    initiator_id = g.current_user.id

    authorization_service.assign_role_to_user(user.id, role.id,
                                              initiator_id=initiator_id)

    flash_success('{} wurde die Rolle "{}" zugewiesen.',
                  user.screen_name, role.title)


@blueprint.route('/<uuid:user_id>/roles/<role_id>', methods=['DELETE'])
@permission_required(RolePermission.assign)
@respond_no_content
def role_deassign(user_id, role_id):
    """Deassign the role from the user."""
    user = _get_user_or_404(user_id)
    role = _get_role_or_404(role_id)
    initiator_id = g.current_user.id

    authorization_service.deassign_role_from_user(user.id, role.id,
                                                  initiator_id=initiator_id)

    flash_success('{} wurde die Rolle "{}" genommen.',
                  user.screen_name, role.title)


@blueprint.route('/<uuid:user_id>/events')
@permission_required(UserPermission.view)
@templated
def view_events(user_id):
    """Show user's events."""
    user = _get_user_or_404(user_id)

    events = service.get_events(user.id)

    return {
        'user': user,
        'events': events,
    }


def _get_user_or_404(user_id):
    user = user_service.find_user_with_details(user_id)

    if user is None:
        abort(404)

    return user


def _get_role_or_404(role_id):
    role = authorization_service.find_role(role_id)

    if role is None:
        abort(404)

    return role
