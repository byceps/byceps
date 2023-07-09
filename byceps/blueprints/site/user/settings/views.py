"""
byceps.blueprints.site.user.settings.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from babel import Locale
from flask import abort, g, request
from flask_babel import force_locale, gettext

from byceps.blueprints.site.orga_team import service as orga_team_service
from byceps.services.brand import brand_setting_service
from byceps.services.connected_external_accounts import (
    connected_external_accounts_service,
)
from byceps.services.country import country_service
from byceps.services.newsletter import newsletter_service
from byceps.services.newsletter.models import ListID as NewsletterListID
from byceps.services.user import (
    user_command_service,
    user_email_address_service,
    user_service,
)
from byceps.signals import user as user_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
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
    user_locale = Locale.parse(user.locale) if user.locale else None
    detail = user_service.get_detail(user.id)

    is_orga = orga_team_service.is_orga_for_current_party(user.id)

    newsletter_list_id = _find_newsletter_list_for_brand()
    newsletter_offered = newsletter_list_id is not None

    subscribed_to_newsletter = newsletter_service.is_subscribed(
        user.id, newsletter_list_id
    )

    discord_account = connected_external_accounts_service.find_connected_external_account_for_user_and_service(
        g.user.id, 'discord'
    )

    return {
        'user': user,
        'user_locale': user_locale,
        'email_address': email_address,
        'detail': detail,
        'is_orga': is_orga,
        'newsletter_offered': newsletter_offered,
        'newsletter_list_id': newsletter_list_id,
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
        current_user, new_email_address, g.site_id
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
    initiator_id = current_user.id

    event = user_command_service.change_screen_name(
        current_user.id, new_screen_name, initiator_id
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
    zip_code = form.zip_code.data.strip()
    city = form.city.data.strip()
    street = form.street.data.strip()
    phone_number = form.phone_number.data.strip()

    event = user_command_service.update_user_details(
        current_user.id,
        first_name,
        last_name,
        date_of_birth,
        country,
        zip_code,
        city,
        street,
        phone_number,
        current_user.id,  # initiator_id
    )

    flash_success(gettext('Your data has been saved.'))

    user_signals.details_updated.send(None, event=event)

    return redirect_to('.view')


def _find_newsletter_list_for_brand() -> NewsletterListID | None:
    """Return the newsletter list configured for this brand, or `None`
    if none is configured.
    """
    value = brand_setting_service.find_setting_value(
        g.brand_id, 'newsletter_list_id'
    )

    if not value:
        return None

    return NewsletterListID(value)
