"""
byceps.blueprints.admin.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from flask import abort, g, request
from flask_babel import gettext

from ....services.authentication.password import authn_password_service
from ....services.authentication.session import authn_session_service
from ....services.authorization import service as authorization_service
from ....services.authorization.transfer.models import (
    Role,
    Permission,
    PermissionID,
)
from ....services.country import service as country_service
from ....services.orga_team import service as orga_team_service
from ....services.shop.order import order_service
from ....services.shop.shop import shop_service
from ....services.site import site_service
from ....services.user import (
    user_command_service,
    user_creation_service,
    user_deletion_service,
    user_email_address_service,
    user_service,
    user_stats_service,
)
from ....services.user.transfer.models import UserForAdmin, UserStateFilter
from ....services.user_badge import user_badge_awarding_service
from ....signals import user as user_signals
from ....util.authorization import permission_registry
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to, respond_no_content

from .forms import (
    ACCOUNT_DELETION_VERIFICATION_TEXT,
    ChangeDetailsForm,
    ChangeEmailAddressForm,
    ChangeScreenNameForm,
    CreateAccountForm,
    DeleteAccountForm,
    InvalidateEmailAddressForm,
    SetPasswordForm,
    SuspendAccountForm,
)
from . import service


blueprint = create_blueprint('user_admin', __name__)


@blueprint.get('/', defaults={'page': 1})
@blueprint.get('/pages/<int:page>')
@permission_required('user.view')
@templated
def index(page):
    """List users."""
    per_page = request.args.get('per_page', type=int, default=20)
    search_term = request.args.get('search_term', default='').strip()
    only = request.args.get('only')

    user_state_filter = UserStateFilter.__members__.get(
        only, UserStateFilter.none
    )

    users = user_service.get_users_paginated(
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


@blueprint.get('/<uuid:user_id>')
@permission_required('user.view')
@templated
def view(user_id):
    """Show a user's interal profile."""
    user = _get_user_for_admin_or_404(user_id)
    db_user = user_service.find_user_with_details(user.id)

    recent_login = authn_session_service.find_recent_login(user.id)
    days_since_recent_login = _calculate_days_since(recent_login)

    orga_activities = orga_team_service.get_orga_activities_for_user(user.id)

    newsletter_subscription_states = list(
        service.get_newsletter_subscription_states(user.id)
    )
    newsletter_subscription_count = sum(
        1 for _, subscribed in newsletter_subscription_states if subscribed
    )

    orders = order_service.get_orders_placed_by_user(user.id)

    order_shop_ids = {order.shop_id for order in orders}
    shops = shop_service.find_shops(order_shop_ids)
    shops_by_id = {shop.id: shop for shop in shops}

    parties_and_tickets = service.get_parties_and_tickets(user.id)
    ticket_count = sum(len(tickets) for _, tickets in parties_and_tickets)

    attended_parties = service.get_attended_parties(user.id)

    badges_with_awarding_quantity = (
        user_badge_awarding_service.get_badges_awarded_to_user(user.id)
    )
    badge_count = len(badges_with_awarding_quantity)

    return {
        'profile_user': user,
        'user': db_user,
        'recent_login': recent_login,
        'days_since_recent_login': days_since_recent_login,
        'orga_activities': orga_activities,
        'newsletter_subscription_count': newsletter_subscription_count,
        'newsletter_subscription_states': newsletter_subscription_states,
        'orders': orders,
        'shops_by_id': shops_by_id,
        'parties_and_tickets': parties_and_tickets,
        'ticket_count': ticket_count,
        'attended_parties': attended_parties,
        'badge_count': badge_count,
        'badges_with_awarding_quantity': badges_with_awarding_quantity,
    }


def _calculate_days_since(dt: Optional[datetime]) -> Optional[int]:
    if dt is None:
        return None

    return (datetime.utcnow().date() - dt.date()).days


# -------------------------------------------------------------------- #
# account


@blueprint.get('/create')
@permission_required('user.create')
@templated
def create_account_form(erroneous_form=None):
    """Show a form to create a user account."""
    form = erroneous_form if erroneous_form else CreateAccountForm()
    form.set_site_choices()

    return {'form': form}


@blueprint.post('/')
@permission_required('user.create')
def create_account():
    """Create a user account."""
    form = CreateAccountForm(request.form)
    form.set_site_choices()

    if not form.validate():
        return create_account_form(form)

    screen_name = form.screen_name.data.strip()
    first_name = form.first_name.data.strip()
    last_name = form.last_name.data.strip()
    email_address = form.email_address.data.lower()
    password = form.password.data
    site_id_for_email = form.site_id.data

    if site_id_for_email:
        site_for_email = site_service.get_site(site_id_for_email)
    else:
        site_for_email = None

    initiator_id = g.user.id

    try:
        user, event = user_creation_service.create_user(
            screen_name,
            email_address,
            password,
            first_name=first_name,
            last_name=last_name,
            creator_id=initiator_id,
            # Do not pass site ID here; the account is not created on a site.
        )
    except user_creation_service.UserCreationFailed:
        flash_error(
            gettext(
                'User "%(screen_name)s" could not be created.',
                screen_name=screen_name,
            )
        )
        return create_account_form(form)

    flash_success(
        gettext(
            'User "%(screen_name)s" has been created.',
            screen_name=user.screen_name,
        )
    )

    if site_for_email:
        user_creation_service.request_email_address_confirmation(
            user, email_address, site_for_email.id
        )
        flash_success(
            gettext('An email has been sent to the corresponding address.'),
            icon='email',
        )

    user_signals.account_created.send(None, event=event)

    return redirect_to('.view', user_id=user.id)


@blueprint.post('/<uuid:user_id>/initialize')
@permission_required('user.administrate')
@respond_no_content
def initialize_account(user_id):
    """Initialize the user account."""
    user = _get_user_or_404(user_id)

    initiator_id = g.user.id

    user_command_service.initialize_account(user.id, initiator_id=initiator_id)

    flash_success(
        gettext(
            "User '%(screen_name)s' has been initialized.",
            screen_name=user.screen_name,
        )
    )


@blueprint.get('/<uuid:user_id>/suspend')
@permission_required('user.administrate')
@templated
def suspend_account_form(user_id, erroneous_form=None):
    """Show form to suspend the user account."""
    user = _get_user_for_admin_or_404(user_id)

    if user.suspended:
        flash_error(
            gettext(
                "User '%(screen_name)s' is already suspended.",
                screen_name=user.screen_name,
            )
        )
        return redirect_to('.view', user_id=user.id)

    form = erroneous_form if erroneous_form else SuspendAccountForm()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
    }


@blueprint.post('/<uuid:user_id>/suspend')
@permission_required('user.administrate')
def suspend_account(user_id):
    """Suspend the user account."""
    user = _get_user_or_404(user_id)

    if user.suspended:
        flash_error(
            gettext(
                "User '%(screen_name)s' is already suspended.",
                screen_name=user.screen_name,
            )
        )
        return redirect_to('.view', user_id=user.id)

    form = SuspendAccountForm(request.form)
    if not form.validate():
        return suspend_account_form(user.id, form)

    initiator_id = g.user.id
    reason = form.reason.data.strip()

    event = user_command_service.suspend_account(user.id, initiator_id, reason)

    user_signals.account_suspended.send(None, event=event)

    flash_success(
        gettext(
            "User '%(screen_name)s' has been suspended.",
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.view', user_id=user.id)


@blueprint.get('/<uuid:user_id>/unsuspend')
@permission_required('user.administrate')
@templated
def unsuspend_account_form(user_id, erroneous_form=None):
    """Show form to unsuspend the user account."""
    user = _get_user_for_admin_or_404(user_id)

    if not user.suspended:
        flash_error(
            gettext(
                "User '%(screen_name)s' is not suspended.",
                screen_name=user.screen_name,
            )
        )
        return redirect_to('.view', user_id=user.id)

    form = erroneous_form if erroneous_form else SuspendAccountForm()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
    }


@blueprint.post('/<uuid:user_id>/unsuspend')
@permission_required('user.administrate')
def unsuspend_account(user_id):
    """Unsuspend the user account."""
    user = _get_user_or_404(user_id)

    if not user.suspended:
        flash_error(
            gettext(
                "User '%(screen_name)s' is not suspended.",
                screen_name=user.screen_name,
            )
        )
        return redirect_to('.view', user_id=user.id)

    form = SuspendAccountForm(request.form)
    if not form.validate():
        return unsuspend_account_form(user.id, form)

    initiator_id = g.user.id
    reason = form.reason.data.strip()

    event = user_command_service.unsuspend_account(
        user.id, initiator_id, reason
    )

    user_signals.account_unsuspended.send(None, event=event)

    flash_success(
        gettext(
            "User '%(screen_name)s' has been unsuspended.",
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.view', user_id=user.id)


@blueprint.get('/<uuid:user_id>/delete')
@permission_required('user.administrate')
@templated
def delete_account_form(user_id, erroneous_form=None):
    """Show form to delete the user account."""
    user = _get_user_for_admin_or_404(user_id)

    if user.deleted:
        flash_error(
            gettext(
                "User '%(screen_name)s' has already been deleted.",
                screen_name=user.screen_name,
            )
        )
        return redirect_to('.view', user_id=user.id)

    form = erroneous_form if erroneous_form else DeleteAccountForm()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
        'verification_text': ACCOUNT_DELETION_VERIFICATION_TEXT,
    }


@blueprint.post('/<uuid:user_id>/delete')
@permission_required('user.administrate')
def delete_account(user_id):
    """Delete the user account."""
    user = _get_user_or_404(user_id)

    if user.deleted:
        flash_error(
            gettext(
                "User '%(screen_name)s' has already been deleted.",
                screen_name=user.screen_name,
            )
        )
        return redirect_to('.view', user_id=user.id)

    form = DeleteAccountForm(request.form)
    if not form.validate():
        return delete_account_form(user.id, form)

    initiator_id = g.user.id
    reason = form.reason.data.strip()

    event = user_deletion_service.delete_account(user.id, initiator_id, reason)

    user_signals.account_deleted.send(None, event=event)

    flash_success(
        gettext(
            "User '%(screen_name)s' has been deleted.",
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.view', user_id=user.id)


# -------------------------------------------------------------------- #
# screen name


@blueprint.get('/<uuid:user_id>/change_screen_name')
@permission_required('user.administrate')
@templated
def change_screen_name_form(user_id, erroneous_form=None):
    """Show form to change the user's screen name."""
    user = _get_user_for_admin_or_404(user_id)

    form = erroneous_form if erroneous_form else ChangeScreenNameForm()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
    }


@blueprint.post('/<uuid:user_id>/change_screen_name')
@permission_required('user.administrate')
def change_screen_name(user_id):
    """Change the user's screen name."""
    user = _get_user_or_404(user_id)

    form = ChangeScreenNameForm(request.form)
    if not form.validate():
        return change_screen_name_form(user.id, form)

    old_screen_name = user.screen_name
    new_screen_name = form.screen_name.data.strip()
    initiator_id = g.user.id
    reason = form.reason.data.strip()

    event = user_command_service.change_screen_name(
        user.id, new_screen_name, initiator_id, reason=reason
    )

    user_signals.screen_name_changed.send(None, event=event)

    flash_success(
        gettext(
            "User '%(old_screen_name)s' has been renamed to '%(new_screen_name)s'.",
            old_screen_name=old_screen_name,
            new_screen_name=new_screen_name,
        )
    )

    return redirect_to('.view', user_id=user.id)


# -------------------------------------------------------------------- #
# email address


@blueprint.get('/<uuid:user_id>/change_email_address')
@permission_required('user.administrate')
@templated
def change_email_address_form(user_id, erroneous_form=None):
    """Show form to change the user's e-mail address."""
    user = _get_user_for_admin_or_404(user_id)

    form = erroneous_form if erroneous_form else ChangeEmailAddressForm()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
    }


@blueprint.post('/<uuid:user_id>/change_email_address')
@permission_required('user.administrate')
def change_email_address(user_id):
    """Change the user's e-mail address."""
    user = _get_user_or_404(user_id)

    form = ChangeEmailAddressForm(request.form)
    if not form.validate():
        return change_email_address_form(user.id, form)

    new_email_address = form.email_address.data.strip()
    verified = False
    initiator_id = g.user.id
    reason = form.reason.data.strip()

    event = user_command_service.change_email_address(
        user.id, new_email_address, verified, initiator_id, reason=reason
    )

    user_signals.email_address_changed.send(None, event=event)

    flash_success(
        gettext(
            "Email address for user '%(screen_name)s' has been updated.",
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.view', user_id=user.id)


@blueprint.get('/<uuid:user_id>/invalidate_email_address')
@permission_required('user.administrate')
@templated
def invalidate_email_address_form(user_id, erroneous_form=None):
    """Show form to invalidate the email address assigned with the account."""
    user = _get_user_for_admin_or_404(user_id)

    email_address = user_service.get_email_address_data(user_id)
    if not email_address.verified:
        flash_error(gettext('Email address is already invalidated.'))
        return redirect_to('.view', user_id=user.id)

    form = erroneous_form if erroneous_form else InvalidateEmailAddressForm()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
    }


@blueprint.post('/<uuid:user_id>/invalidate_email_address')
@permission_required('user.administrate')
def invalidate_email_address(user_id):
    """Invalidate the email address assigned with the account."""
    user = _get_user_or_404(user_id)

    email_address = user_service.get_email_address_data(user_id)
    if not email_address.verified:
        flash_error(gettext('Email address is already invalidated.'))
        return redirect_to('.view', user_id=user.id)

    form = InvalidateEmailAddressForm(request.form)
    if not form.validate():
        return invalidate_email_address_form(user.id, form)

    initiator_id = g.user.id
    reason = form.reason.data.strip()

    event = user_email_address_service.invalidate_email_address(
        user.id, reason, initiator_id=initiator_id
    )

    user_signals.email_address_invalidated.send(None, event=event)

    flash_success(
        gettext(
            "The email address of user '%(screen_name)s' has been invalidated.",
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.view', user_id=user.id)


# -------------------------------------------------------------------- #
# details


@blueprint.get('/<uuid:user_id>/details')
@permission_required('user.administrate')
@templated
def change_details_form(user_id, erroneous_form=None):
    """Show a form to change the user's details."""
    user = _get_user_for_admin_or_404(user_id)

    detail = user_service.get_detail(user_id)

    form = erroneous_form if erroneous_form else ChangeDetailsForm(obj=detail)
    country_names = country_service.get_country_names()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
        'country_names': country_names,
    }


@blueprint.post('/<uuid:user_id>/details')
@permission_required('user.administrate')
def change_details(user_id):
    """Change the user's details."""
    user = _get_user_or_404(user_id)

    form = ChangeDetailsForm(request.form)
    if not form.validate():
        return change_details_form(user.id, form)

    first_name = form.first_name.data.strip()
    last_name = form.last_name.data.strip()
    date_of_birth = form.date_of_birth.data
    country = form.country.data.strip()
    zip_code = form.zip_code.data.strip()
    city = form.city.data.strip()
    street = form.street.data.strip()
    phone_number = form.phone_number.data.strip()

    event = user_command_service.update_user_details(
        user.id,
        first_name,
        last_name,
        date_of_birth,
        country,
        zip_code,
        city,
        street,
        phone_number,
        g.user.id,  # initiator_id
    )

    flash_success(gettext('Changes have been saved.'))

    user_signals.details_updated.send(None, event=event)

    return redirect_to('.view', user_id=user.id)


# -------------------------------------------------------------------- #
# authentication


@blueprint.get('/<uuid:user_id>/password')
@permission_required('user.set_password')
@templated
def set_password_form(user_id, erroneous_form=None):
    """Show a form to set a new password for the user."""
    user = _get_user_for_admin_or_404(user_id)

    form = erroneous_form if erroneous_form else SetPasswordForm()

    return {
        'profile_user': user,
        'user': user,
        'form': form,
    }


@blueprint.post('/<uuid:user_id>/password')
@permission_required('user.set_password')
def set_password(user_id):
    """Set a new password for the user."""
    user = _get_user_or_404(user_id)

    form = SetPasswordForm(request.form)
    if not form.validate():
        return set_password_form(user.id, form)

    new_password = form.password.data
    initiator_id = g.user.id

    authn_password_service.update_password_hash(
        user.id, new_password, initiator_id
    )

    flash_success(
        gettext(
            "New password has been set for user '%(screen_name)s'.",
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.view', user_id=user.id)


# -------------------------------------------------------------------- #
# authorization


@blueprint.get('/<uuid:user_id>/permissions')
@permission_required('user.view')
@templated
def view_permissions(user_id):
    """Show user's permissions."""
    user = _get_user_for_admin_or_404(user_id)

    user_permission_ids_by_role = (
        authorization_service.get_permission_ids_by_role_for_user(user.id)
    )

    permissions_by_role = _index_permissions_by_role(
        user_permission_ids_by_role
    )

    return {
        'profile_user': user,
        'user': user,
        'permissions_by_role': permissions_by_role,
    }


@blueprint.get('/<uuid:user_id>/roles/assignment')
@permission_required('role.assign')
@templated
def manage_roles(user_id):
    """Manage what roles are assigned to the user."""
    user = _get_user_for_admin_or_404(user_id)

    permission_ids_by_role = authorization_service.get_permission_ids_by_role()

    permissions_by_role = _index_permissions_by_role(permission_ids_by_role)

    user_role_ids = authorization_service.find_role_ids_for_user(user.id)

    return {
        'profile_user': user,
        'user': user,
        'permissions_by_role': permissions_by_role,
        'user_role_ids': user_role_ids,
    }


def _index_permissions_by_role(
    permission_ids_by_role: dict[Role, frozenset[PermissionID]]
) -> dict[Role, frozenset[Permission]]:
    registered_permissions_by_id = {
        permission.id: permission
        for permission in permission_registry.get_registered_permissions()
    }

    return {
        role: frozenset(
            registered_permissions_by_id[permission_id]
            for permission_id in permission_ids
            if permission_id in registered_permissions_by_id
        )
        for role, permission_ids in permission_ids_by_role.items()
    }


@blueprint.post('/<uuid:user_id>/roles/<role_id>')
@permission_required('role.assign')
@respond_no_content
def role_assign(user_id, role_id):
    """Assign the role to the user."""
    user = _get_user_or_404(user_id)
    role = _get_role_or_404(role_id)
    initiator_id = g.user.id

    authorization_service.assign_role_to_user(
        role.id, user.id, initiator_id=initiator_id
    )

    flash_success(
        gettext(
            '%(role_title)s has been assigned to "%(screen_name)s".',
            screen_name=user.screen_name,
            role_title=role.title,
        )
    )


@blueprint.delete('/<uuid:user_id>/roles/<role_id>')
@permission_required('role.assign')
@respond_no_content
def role_deassign(user_id, role_id):
    """Deassign the role from the user."""
    user = _get_user_or_404(user_id)
    role = _get_role_or_404(role_id)
    initiator_id = g.user.id

    authorization_service.deassign_role_from_user(
        role.id, user.id, initiator_id=initiator_id
    )

    flash_success(
        gettext(
            '%(role_title)s has been withdrawn from "%(screen_name)s".',
            screen_name=user.screen_name,
            role_title=role.title,
        )
    )


# -------------------------------------------------------------------- #
# events


@blueprint.get('/<uuid:user_id>/events')
@permission_required('user.view')
@templated
def view_events(user_id):
    """Show user's events."""
    user = _get_user_for_admin_or_404(user_id)

    log_entries = list(service.get_log_entries(user.id))

    include_logins = request.args.get('include_logins', default='yes') == 'yes'
    if not include_logins:
        log_entries = [
            entry
            for entry in log_entries
            if entry['event_type'] != 'user-logged-in'
        ]

    return {
        'profile_user': user,
        'user': user,
        'log_entries': log_entries,
        'logins_included': include_logins,
    }


# -------------------------------------------------------------------- #
# helpers


def _get_user_for_admin_or_404(user_id) -> UserForAdmin:
    user = user_service.find_user_for_admin(user_id)

    if user is None:
        abort(404)

    return user


def _get_user_or_404(user_id):
    user = user_service.find_user(user_id)

    if user is None:
        abort(404)

    return user


def _get_role_or_404(role_id):
    role = authorization_service.find_role(role_id)

    if role is None:
        abort(404)

    return role
