"""
byceps.blueprints.common.authentication.password.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask import abort, g, request

from .....config import get_app_mode
from .....services.authentication.password import (
    reset_service as password_reset_service,
    service as password_service,
)
from .....services.email import service as email_service
from .....services.email.transfer.models import Sender
from .....services.site import service as site_service
from .....services.user import service as user_service
from .....services.verification_token import (
    service as verification_token_service,
)
from .....services.verification_token.models import Token as VerificationToken
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.views import redirect_to

from .forms import RequestResetForm, ResetForm, UpdateForm


blueprint = create_blueprint('authentication.password', __name__)


# -------------------------------------------------------------------- #
# password update


@blueprint.route('/update')
@templated
def update_form(erroneous_form=None):
    """Show a form to update the current user's password."""
    _get_current_user_or_404()

    form = erroneous_form if erroneous_form else UpdateForm()

    return {'form': form}


@blueprint.route('/', methods=['POST'])
def update():
    """Update the current user's password."""
    user = _get_current_user_or_404()

    form = UpdateForm(request.form)

    if not form.validate():
        return update_form(form)

    password = form.new_password.data

    password_service.update_password_hash(user.id, password, user.id)

    flash_success('Dein Passwort wurde geändert. Bitte melde dich erneut an.')
    return redirect_to('authentication.login_form')


# -------------------------------------------------------------------- #
# password reset


@blueprint.route('/reset/request')
@templated
def request_reset_form(erroneous_form=None):
    """Show a form to request a password reset."""
    form = erroneous_form if erroneous_form else RequestResetForm()

    return {'form': form}


@blueprint.route('/reset/request', methods=['POST'])
def request_reset():
    """Request a password reset."""
    form = RequestResetForm(request.form)
    if not form.validate():
        return request_reset_form(form)

    screen_name = form.screen_name.data.strip()
    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

    if (user is None) or user.deleted:
        flash_error(f'Der Benutzername "{screen_name}" ist unbekannt.')
        return request_reset_form(form)

    if user.email_address is None:
        flash_error(
            f'Für das Benutzerkonto "{screen_name}" ist keine E-Mail-Adresse hinterlegt.'
        )
        return request_reset_form(form)

    if not user.email_address_verified:
        flash_error(
            f'Die E-Mail-Adresse für das Benutzerkonto "{screen_name}" '
            'wurde noch nicht bestätigt.'
        )
        return redirect_to('user_email_address.request_confirmation_email')

    if user.suspended:
        flash_error(f'Das Benutzerkonto "{screen_name}" ist gesperrt.')
        return request_reset_form(form)

    sender = _get_sender()

    password_reset_service.prepare_password_reset(
        user, request.url_root, sender=sender
    )

    flash_success(
        'Ein Link zum Setzen eines neuen Passworts '
        f'für den Benutzernamen "{user.screen_name}" '
        'wurde an die hinterlegte E-Mail-Adresse versendet.'
    )
    return request_reset_form()


def _get_sender() -> Optional[Sender]:
    if not get_app_mode().is_site():
        return None

    site = site_service.get_site(g.site_id)
    email_config = email_service.get_config(site.brand_id)
    return email_config.sender


@blueprint.route('/reset/token/<token>')
@templated
def reset_form(token, erroneous_form=None):
    """Show a form to reset the current user's password."""
    _verify_reset_token(token)

    form = erroneous_form if erroneous_form else ResetForm()

    return {
        'form': form,
        'token': token,
    }


@blueprint.route('/reset/token/<token>', methods=['POST'])
def reset(token):
    """Reset the current user's password."""
    verification_token = _verify_reset_token(token)

    form = ResetForm(request.form)
    if not form.validate():
        return reset_form(token, form)

    password = form.new_password.data

    password_reset_service.reset_password(verification_token, password)

    flash_success('Das Passwort wurde geändert.')
    return redirect_to('authentication.login_form')


def _verify_reset_token(token: str) -> VerificationToken:
    verification_token = (
        verification_token_service.find_for_password_reset_by_token(token)
    )

    if not _is_verification_token_valid(verification_token):
        flash_error(
            'Es wurde kein gültiges Token angegeben. '
            'Ein Token ist nur 24 Stunden lang gültig.'
        )
        abort(404)

    user = user_service.find_active_user(verification_token.user_id)
    if user is None:
        flash_error('Es wurde kein gültiges Token angegeben.')
        abort(404)

    return verification_token


def _is_verification_token_valid(token: Optional[VerificationToken]) -> bool:
    return (token is not None) and not token.is_expired


# -------------------------------------------------------------------- #
# helpers


def _get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
