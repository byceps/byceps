"""
byceps.blueprints.user.current.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, jsonify, request, Response

from ....config import get_app_mode
from ....services.country import service as country_service
from ....services.newsletter import service as newsletter_service
from ....services.user import command_service as user_command_service
from ....services.user import service as user_service
from ....signals import user as user_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from ...authentication.decorators import login_required

from ..creation.views import _find_newsletter_list_for_brand

from .forms import DetailsForm, ChangeScreenNameForm


blueprint = create_blueprint('user_current', __name__)


@blueprint.route('/me')
@login_required
@templated
def view():
    """Show the current user's internal profile."""
    current_user = g.current_user

    user = user_service.find_active_db_user(current_user.id)
    if user is None:
        abort(404)

    if get_app_mode().is_site():
        newsletter_list_id = _find_newsletter_list_for_brand()
        newsletter_offered = newsletter_list_id is not None

        subscribed_to_newsletter = newsletter_service.is_subscribed(
            user.id, newsletter_list_id
        )
    else:
        newsletter_list_id = None
        newsletter_offered = False
        subscribed_to_newsletter = None

    return {
        'user': user,
        'newsletter_offered': newsletter_offered,
        'newsletter_list_id': newsletter_list_id,
        'subscribed_to_newsletter': subscribed_to_newsletter,
    }


@blueprint.route('/me.json')
def view_as_json():
    """Show selected attributes of the current user's profile as JSON."""
    if get_app_mode().is_admin():
        abort(404)

    user = g.current_user

    if not user.is_active:
        # Return empty response.
        return Response(status=403)

    return jsonify(
        {
            'id': user.id,
            'screen_name': user.screen_name,
            'avatar_url': user.avatar_url,
        }
    )


@blueprint.route('/me/screen_name')
@templated
def change_screen_name_form(erroneous_form=None):
    """Show a form to change the current user's screen name."""
    _get_current_user_or_404()

    form = erroneous_form if erroneous_form else ChangeScreenNameForm()

    return {
        'form': form,
    }


@blueprint.route('/me/screen_name', methods=['POST'])
def change_screen_name():
    """Change the current user's screen name."""
    current_user = _get_current_user_or_404()

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

    flash_success(f'Dein Benutzername wurde zu "{new_screen_name}" geändert.')

    return redirect_to('.view')


@blueprint.route('/me/details')
@templated
def details_update_form(erroneous_form=None):
    """Show a form to update the current user's details."""
    current_user = _get_current_user_or_404()
    user = user_service.find_user_with_details(current_user.id)

    form = erroneous_form if erroneous_form else DetailsForm(obj=user.detail)
    country_names = country_service.get_country_names()

    return {
        'form': form,
        'country_names': country_names,
    }


@blueprint.route('/me/details', methods=['POST'])
def details_update():
    """Update the current user's details."""
    current_user = _get_current_user_or_404()

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

    flash_success('Deine Daten wurden gespeichert.')

    user_signals.details_updated.send(None, event=event)

    return redirect_to('.view')


def _get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
