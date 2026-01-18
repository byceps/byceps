"""
byceps.services.user.settings.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from babel import Locale
from flask import abort, g, request
from flask_babel import force_locale, gettext

from byceps.services.brand import brand_service
from byceps.services.external_accounts import external_accounts_service
from byceps.services.country import country_service
from byceps.services.newsletter import newsletter_service
from byceps.services.orga_team import orga_team_service
from byceps.services.user import (
    signals as user_signals,
    user_command_service,
    user_email_address_service,
    user_service,
)
from byceps.services.user.errors import NothingChangedError
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.result import Err, Ok
from byceps.util.views import login_required, redirect_to, respond_no_content

from .forms import ChangeEmailAddressForm, ChangeScreenNameForm, DetailsForm


blueprint = create_blueprint('user_settings', __name__)


@blueprint.get('')
@login_required
@templated
def view():
    """Show the current user's internal profile."""
    user = user_service.find_active_user(g.user.id, include_avatar=True)
    if user is None:
        abort(404)

    email_address = user_service.find_email_address(user.id)
    detail = user_service.get_detail(user.id)

    is_orga = orga_team_service.is_orga_for_party(user.id, g.party.id)

    newsletter_list = brand_service.find_newsletter_list_for_brand(
        g.site.brand_id
    )
    newsletter_offered = newsletter_list is not None

    subscribed_to_newsletter = (
        newsletter_offered
        and newsletter_service.is_user_subscribed_to_list(
            user.id, newsletter_list.id
        )
    )

    discord_account = external_accounts_service.find_connected_external_account_for_user_and_service(
        g.user.id, 'discord'
    )

    return {
        'user': user,
        'email_address': email_address,
        'detail': detail,
        'is_orga': is_orga,
        'newsletter_offered': newsletter_offered,
        'newsletter_list': newsletter_list,
        'subscribed_to_newsletter': subscribed_to_newsletter,
        'discord_account': discord_account,
    }


@blueprint.get('/email_address')
@login_required
@templated
def change_email_address_form(erroneous_form=None):
    """Show a form to change the current user's email address."""
    form = erroneous_form if erroneous_form else ChangeEmailAddressForm()

    return {
        'form': form,
    }


@blueprint.post('/email_address')
@login_required
def change_email_address():
    """Request a change of the current user's email address."""
    current_user = g.user

    form = ChangeEmailAddressForm(request.form)
    if not form.validate():
        return change_email_address_form(form)

    new_email_address = form.new_email_address.data.strip()

    user_email_address_service.send_email_address_change_email_for_site(
        current_user, new_email_address, g.site.id
    )

    flash_success(
        gettext(
            'An email with a verification link has been sent to your new '
            'address. The email address of your account will be changed '
            'to the new address once you visit the link to verify it.'
        )
    )

    return redirect_to('.view')


@blueprint.get('/screen_name')
@login_required
@templated
def change_screen_name_form(erroneous_form=None):
    """Show a form to change the current user's screen name."""
    form = erroneous_form if erroneous_form else ChangeScreenNameForm()

    return {
        'form': form,
    }


@blueprint.post('/screen_name')
@login_required
def change_screen_name():
    """Change the current user's screen name."""
    current_user = g.user

    form = ChangeScreenNameForm(request.form)
    if not form.validate():
        return change_screen_name_form(form)

    new_screen_name = form.screen_name.data.strip()
    initiator = current_user

    event = user_command_service.change_screen_name(
        current_user, new_screen_name, initiator
    )

    user_signals.screen_name_changed.send(None, event=event)

    flash_success(
        gettext(
            'Your username has been changed to "%(new_screen_name)s".',
            new_screen_name=new_screen_name,
        )
    )

    return redirect_to('.view')


@blueprint.post('/locale')
@login_required
@respond_no_content
def update_locale():
    """Update the current user's locale."""
    locale_str = request.args.get('locale')
    if locale_str:
        locale = Locale.parse(locale_str)
    else:
        locale = None

    user_command_service.update_locale(g.user.id, locale)

    if locale:
        with force_locale(locale):
            flash_success(gettext('Your language preference has been updated.'))
    else:
        flash_success(gettext('Your language preference has been updated.'))


@blueprint.get('/details')
@login_required
@templated
def details_update_form(erroneous_form=None):
    """Show a form to update the current user's details."""
    detail = user_service.get_detail(g.user.id)

    form = erroneous_form if erroneous_form else DetailsForm(obj=detail)
    country_names = country_service.get_country_names()

    return {
        'form': form,
        'country_names': country_names,
    }


@blueprint.post('/details')
@login_required
def details_update():
    """Update the current user's details."""
    current_user = g.user

    form = DetailsForm(request.form)

    if not form.validate():
        return details_update_form(form)

    first_name = form.first_name.data.strip()
    last_name = form.last_name.data.strip()
    date_of_birth = form.date_of_birth.data
    country = form.country.data.strip()
    postal_code = form.postal_code.data.strip()
    city = form.city.data.strip()
    street = form.street.data.strip()
    phone_number = form.phone_number.data.strip()
    initiator = current_user

    update_result = user_command_service.update_user_details(
        current_user.id,
        first_name,
        last_name,
        date_of_birth,
        country,
        postal_code,
        city,
        street,
        phone_number,
        initiator,
    )

    match update_result:
        case Ok(event):
            flash_success(gettext('Changes have been saved.'))
            user_signals.details_updated.send(None, event=event)
        case Err(NothingChangedError()):
            flash_notice(gettext('Nothing has been changed.'))
        case Err(msg):
            flash_error(gettext('An unexpected error occurred.') + '\n' + msg)

    return redirect_to('.view')
