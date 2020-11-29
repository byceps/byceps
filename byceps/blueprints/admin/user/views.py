"""
byceps.blueprints.admin.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from flask import abort, g, request

from ....services.authentication.password import service as password_service
from ....services.authentication.session import service as session_service
from ....services.authorization import service as authorization_service
from ....services.orga_team import service as orga_team_service
from ....services.shop.order import service as order_service
from ....services.shop.shop import service as shop_service
from ....services.site import service as site_service
from ....services.user import command_service as user_command_service
from ....services.user import creation_service as user_creation_service
from ....services.user import service as user_service
from ....services.user import stats_service as user_stats_service
from ....services.user_badge import awarding_service as badge_awarding_service
from ....signals import user as user_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to, respond_no_content

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry

from ..authorization.authorization import RolePermission

from .authorization import UserPermission
from .forms import (
    ChangeEmailAddressForm,
    ChangeScreenNameForm,
    CreateAccountForm,
    DeleteAccountForm,
    SetPasswordForm,
    SuspendAccountForm,
)
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

    user_state_filter = UserStateFilter.__members__.get(
        only, UserStateFilter.none
    )

    users = service.get_users_paginated(
        page, per_page, search_term=search_term, state_filter=user_state_filter
    )

    total_active = user_stats_service.count_active_users()
    total_uninitialized = user_stats_service.count_uninitialized_users()
    total_suspended = user_stats_service.count_suspended_users()
    total_deleted = user_stats_service.count_deleted_users()
    total_overall = user_stats_service.count_users()

    return {
        'users': users,
        'total_active': total_active,
        'total_uninitialized': total_uninitialized,
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

    recent_login = session_service.find_recent_login(user.id)
    days_since_recent_login = _calculate_days_since(recent_login)

    orga_activities = orga_team_service.get_orga_activities_for_user(user.id)

    newsletter_subscriptions = service.get_newsletter_subscriptions(user.id)

    orders = order_service.get_orders_placed_by_user(user.id)

    order_shop_ids = {order.shop_id for order in orders}
    shops = shop_service.find_shops(order_shop_ids)
    shops_by_id = {shop.id: shop for shop in shops}

    parties_and_tickets = service.get_parties_and_tickets(user.id)

    attended_parties = service.get_attended_parties(user.id)

    badges_with_awarding_quantity = badge_awarding_service.get_badges_awarded_to_user(
        user.id
    )

    return {
        'user': user,
        'recent_login': recent_login,
        'days_since_recent_login': days_since_recent_login,
        'orga_activities': orga_activities,
        'newsletter_subscriptions': newsletter_subscriptions,
        'orders': orders,
        'shops_by_id': shops_by_id,
        'parties_and_tickets': parties_and_tickets,
        'attended_parties': attended_parties,
        'badges_with_awarding_quantity': badges_with_awarding_quantity,
    }


def _calculate_days_since(dt: Optional[datetime]) -> Optional[int]:
    if dt is None:
        return None

    return (datetime.utcnow().date() - dt.date()).days


@blueprint.route('/create')
@permission_required(UserPermission.create)
@templated
def create_account_form(erroneous_form=None):
    """Show a form to create a user account."""
    form = erroneous_form if erroneous_form else CreateAccountForm()
    form.set_site_choices()

    return {'form': form}


@blueprint.route('/', methods=['POST'])
@permission_required(UserPermission.create)
def create_account():
    """Create a user account."""
    form = CreateAccountForm(request.form)
    form.set_site_choices()

    if not form.validate():
        return create_account_form(form)

    screen_name = form.screen_name.data.strip()
    first_names = form.first_names.data.strip()
    last_name = form.last_name.data.strip()
    email_address = form.email_address.data.lower()
    password = form.password.data
    site_id = form.site_id.data

    if site_id:
        site = site_service.get_site(site_id)
    else:
        site = None

    if user_service.is_screen_name_already_assigned(screen_name):
        flash_error(
            'Dieser Benutzername ist bereits einem Benutzerkonto zugeordnet.'
        )
        return create_account_form(form)

    if user_service.is_email_address_already_assigned(email_address):
        flash_error(
            'Diese E-Mail-Adresse ist bereits einem Benutzerkonto zugeordnet.'
        )
        return create_account_form(form)

    initiator_id = g.current_user.id

    try:
        user, event = user_creation_service.create_basic_user(
            screen_name,
            email_address,
            password,
            first_names=first_names,
            last_name=last_name,
            creator_id=initiator_id,
        )
    except user_creation_service.UserCreationFailed:
        flash_error(
            f'Das Benutzerkonto für "{screen_name}" '
            'konnte nicht angelegt werden.'
        )
        return create_account_form(form)

    flash_success(f'Das Benutzerkonto "{user.screen_name}" wurde angelegt.')

    if site:
        user_creation_service.request_email_address_confirmation(
            user, email_address, site_id
        )
        flash_success(
            f'Eine E-Mail wurde an die hinterlegte Adresse versendet.',
            icon='email',
        )

    user_signals.account_created.send(None, event=event)

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

    flash_success(
        f"Für Benutzerkonto '{user.screen_name}' wurde "
        "ein neues Passwort gesetzt."
    )

    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/initialize', methods=['POST'])
@permission_required(UserPermission.administrate)
@respond_no_content
def initialize_account(user_id):
    """Initialize the user account."""
    user = _get_user_or_404(user_id)

    initiator_id = g.current_user.id

    user_command_service.initialize_account(user.id, initiator_id=initiator_id)

    flash_success(
        f"Das Benutzerkonto '{user.screen_name}' wurde initialisiert."
    )


@blueprint.route('/<uuid:user_id>/suspend')
@permission_required(UserPermission.administrate)
@templated
def suspend_account_form(user_id, erroneous_form=None):
    """Show form to suspend the user account."""
    user = _get_user_or_404(user_id)

    if user.suspended:
        flash_error(
            f"Das Benutzerkonto '{user.screen_name}' ist bereits gesperrt."
        )
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
        flash_error(
            f"Das Benutzerkonto '{user.screen_name}' ist bereits gesperrt."
        )
        return redirect_to('.view', user_id=user.id)

    form = SuspendAccountForm(request.form)
    if not form.validate():
        return suspend_account_form(user.id, form)

    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    event = user_command_service.suspend_account(user.id, initiator_id, reason)

    user_signals.account_suspended.send(None, event=event)

    flash_success(f"Das Benutzerkonto '{user.screen_name}' wurde gesperrt.")
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/unsuspend')
@permission_required(UserPermission.administrate)
@templated
def unsuspend_account_form(user_id, erroneous_form=None):
    """Show form to unsuspend the user account."""
    user = _get_user_or_404(user_id)

    if not user.suspended:
        flash_error(
            f"Das Benutzerkonto '{user.screen_name}' ist bereits entsperrt."
        )
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
        flash_error(
            f"Das Benutzerkonto '{user.screen_name}' ist bereits entsperrt."
        )
        return redirect_to('.view', user_id=user.id)

    form = SuspendAccountForm(request.form)
    if not form.validate():
        return unsuspend_account_form(user.id, form)

    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    event = user_command_service.unsuspend_account(
        user.id, initiator_id, reason
    )

    user_signals.account_unsuspended.send(None, event=event)

    flash_success(f"Das Benutzerkonto '{user.screen_name}' wurde entsperrt.")
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/delete')
@permission_required(UserPermission.administrate)
@templated
def delete_account_form(user_id, erroneous_form=None):
    """Show form to delete the user account."""
    user = _get_user_or_404(user_id)

    if user.deleted:
        flash_error(
            f"Das Benutzerkonto '{user.screen_name}' "
            "ist bereits gelöscht worden."
        )
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
        flash_error(
            f"Das Benutzerkonto '{user.screen_name}' "
            "ist bereits gelöscht worden."
        )
        return redirect_to('.view', user_id=user.id)

    form = DeleteAccountForm(request.form)
    if not form.validate():
        return delete_account_form(user.id, form)

    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    event = user_command_service.delete_account(user.id, initiator_id, reason)

    user_signals.account_deleted.send(None, event=event)

    flash_success(f"Das Benutzerkonto '{user.screen_name}' wurde gelöscht.")
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/change_email_address')
@permission_required(UserPermission.administrate)
@templated
def change_email_address_form(user_id, erroneous_form=None):
    """Show form to change the user's e-mail address."""
    user = _get_user_or_404(user_id)

    form = erroneous_form if erroneous_form else ChangeEmailAddressForm()

    return {
        'user': user,
        'form': form,
    }


@blueprint.route('/<uuid:user_id>/change_email_address', methods=['POST'])
@permission_required(UserPermission.administrate)
def change_email_address(user_id):
    """Change the user's e-mail address."""
    user = _get_user_or_404(user_id)

    form = ChangeEmailAddressForm(request.form)
    if not form.validate():
        return change_email_address_form(user.id, form)

    old_email_address = user.email_address
    new_email_address = form.email_address.data.strip()
    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    event = user_command_service.change_email_address(
        user.id, new_email_address, initiator_id, reason=reason
    )

    user_signals.email_address_changed.send(None, event=event)

    flash_success(
        f"Die E-Mail-Adresse des Benutzerkontos '{user.screen_name}' wurde "
        f"geändert."
    )
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/change_screen_name')
@permission_required(UserPermission.administrate)
@templated
def change_screen_name_form(user_id, erroneous_form=None):
    """Show form to change the user's screen name."""
    user = _get_user_or_404(user_id)

    form = erroneous_form if erroneous_form else ChangeScreenNameForm()

    return {
        'user': user,
        'form': form,
    }


@blueprint.route('/<uuid:user_id>/change_screen_name', methods=['POST'])
@permission_required(UserPermission.administrate)
def change_screen_name(user_id):
    """Change the user's screen name."""
    user = _get_user_or_404(user_id)

    form = ChangeScreenNameForm(request.form)
    if not form.validate():
        return change_screen_name_form(user.id, form)

    old_screen_name = user.screen_name
    new_screen_name = form.screen_name.data.strip()
    initiator_id = g.current_user.id
    reason = form.reason.data.strip()

    event = user_command_service.change_screen_name(
        user.id, new_screen_name, initiator_id, reason=reason
    )

    user_signals.screen_name_changed.send(None, event=event)

    flash_success(
        f"Das Benutzerkonto '{old_screen_name}' wurde "
        f"umbenannt in '{new_screen_name}'."
    )
    return redirect_to('.view', user_id=user.id)


@blueprint.route('/<uuid:user_id>/permissions')
@permission_required(UserPermission.view)
@templated
def view_permissions(user_id):
    """Show user's permissions."""
    user = _get_user_or_404(user_id)

    permissions_by_role = authorization_service.get_permissions_by_roles_for_user_with_titles(
        user.id
    )

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

    permissions_by_role = (
        authorization_service.get_permissions_by_roles_with_titles()
    )

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

    authorization_service.assign_role_to_user(
        role.id, user.id, initiator_id=initiator_id
    )

    flash_success(
        f'{user.screen_name} wurde die Rolle "{role.title}" zugewiesen.'
    )


@blueprint.route('/<uuid:user_id>/roles/<role_id>', methods=['DELETE'])
@permission_required(RolePermission.assign)
@respond_no_content
def role_deassign(user_id, role_id):
    """Deassign the role from the user."""
    user = _get_user_or_404(user_id)
    role = _get_role_or_404(role_id)
    initiator_id = g.current_user.id

    authorization_service.deassign_role_from_user(
        role.id, user.id, initiator_id=initiator_id
    )

    flash_success(
        f'{user.screen_name} wurde die Rolle "{role.title}" genommen.'
    )


@blueprint.route('/<uuid:user_id>/events')
@permission_required(UserPermission.view)
@templated
def view_events(user_id):
    """Show user's events."""
    user = _get_user_or_404(user_id)

    events = list(service.get_events(user.id))

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
