"""
byceps.blueprints.site.user.settings.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask import abort, g, request
from flask_babel import gettext

from .....services.brand import settings_service as brand_settings_service
from .....services.country import service as country_service
from .....services.newsletter import service as newsletter_service
from .....services.newsletter.transfer.models import ListID as NewsletterListID
from .....services.user import command_service as user_command_service
from .....services.user import service as user_service
from .....signals import user as user_signals
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.views import login_required, redirect_to

from .forms import DetailsForm, ChangeScreenNameForm


blueprint = create_blueprint('user_settings', __name__)


@blueprint.get('')
@login_required
@templated
def view():
    """Show the current user's internal profile."""
    user = user_service.find_active_db_user(g.user.id)
    if user is None:
        abort(404)

    newsletter_list_id = _find_newsletter_list_for_brand()
    newsletter_offered = newsletter_list_id is not None

    subscribed_to_newsletter = newsletter_service.is_subscribed(
        user.id, newsletter_list_id
    )

    return {
        'user': user,
        'newsletter_offered': newsletter_offered,
        'newsletter_list_id': newsletter_list_id,
        'subscribed_to_newsletter': subscribed_to_newsletter,
    }


@blueprint.get('/screen_name')
@login_required
@templated
def change_screen_name_form(erroneous_form=None):
    """Show a form to change the current user's screen name."""
    form = erroneous_form if erroneous_form else ChangeScreenNameForm()

    return {
        'form': form,
    }


@login_required
@blueprint.post('/screen_name')
def change_screen_name():
    """Change the current user's screen name."""
    current_user = g.user

    form = ChangeScreenNameForm(request.form)
    if not form.validate():
        return change_screen_name_form(form)

    old_screen_name = current_user.screen_name
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


@blueprint.get('/details')
@login_required
@templated
def details_update_form(erroneous_form=None):
    """Show a form to update the current user's details."""
    user = user_service.find_user_with_details(g.user.id)

    form = erroneous_form if erroneous_form else DetailsForm(obj=user.detail)
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

    first_names = form.first_names.data.strip()
    last_name = form.last_name.data.strip()
    date_of_birth = form.date_of_birth.data
    country = form.country.data.strip()
    zip_code = form.zip_code.data.strip()
    city = form.city.data.strip()
    street = form.street.data.strip()
    phone_number = form.phone_number.data.strip()

    event = user_command_service.update_user_details(
        current_user.id,
        first_names,
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


def _find_newsletter_list_for_brand() -> Optional[NewsletterListID]:
    """Return the newsletter list configured for this brand, or `None`
    if none is configured.
    """
    value = brand_settings_service.find_setting_value(
        g.brand_id, 'newsletter_list_id'
    )

    if not value:
        return None

    return NewsletterListID(value)
