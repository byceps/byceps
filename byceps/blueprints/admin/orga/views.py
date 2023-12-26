"""
byceps.blueprints.admin.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.orga import orga_birthday_service, orga_service
from byceps.services.orga.models import Birthday
from byceps.services.user import user_service
from byceps.signals import orga as orga_signals
from byceps.util.export import serialize_dicts_to_csv
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
    textified,
)

from .forms import GrantOrgaStatusForm


blueprint = create_blueprint('orga_admin', __name__)


@blueprint.get('/persons/<brand_id>')
@permission_required('orga_detail.view')
@templated
def persons_for_brand(brand_id):
    """List organizers for the brand with details."""
    brand = _get_brand_or_404(brand_id)

    orgas = orga_service.get_orgas_for_brand(brand.id)
    orgas.sort(key=user_service.get_sort_key_for_screen_name)

    orgas_with_birthdays = [(user, _to_birthday(user)) for user in orgas]

    return {
        'brand': brand,
        'orgas_with_birthdays': orgas_with_birthdays,
    }


def _to_birthday(user) -> Birthday | None:
    dob = user.detail.date_of_birth

    if dob is None:
        return None

    return Birthday(dob)


@blueprint.get('/persons/<brand_id>/create')
@permission_required('orga_team.administrate_memberships')
@templated
def grant_orga_status_form(brand_id, erroneous_form=None):
    """Show form to grant organizer status to a user for the brand."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else GrantOrgaStatusForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/persons/<brand_id>')
@permission_required('orga_team.administrate_memberships')
def grant_orga_status(brand_id):
    """Grant organizer status to the user for the brand."""
    brand = _get_brand_or_404(brand_id)

    form = GrantOrgaStatusForm(request.form, brand_id=brand.id)
    if not form.validate():
        return grant_orga_status_form(brand.id, form)

    user = form.user.data
    initiator = g.user

    event = orga_service.grant_orga_status(user, brand, initiator)

    orga_signals.orga_status_granted.send(None, event=event)

    flash_success(
        gettext(
            'Organizer status was granted to %(screen_name)s for brand %(brand_title)s.',
            screen_name=event.user.screen_name,
            brand_title=event.brand.title,
        )
    )

    return redirect_to('.persons_for_brand', brand_id=event.brand.id)


@blueprint.delete('/persons/<brand_id>/<uuid:user_id>')
@permission_required('orga_team.administrate_memberships')
@respond_no_content
def revoke_orga_status(brand_id, user_id):
    """Revoke the user's organizer status for the brand."""
    orga_flag = orga_service.find_orga_flag(user_id, brand_id)

    if orga_flag is None:
        abort(404)

    user = orga_flag.user
    brand = orga_flag.brand
    initiator = g.user

    event = orga_service.revoke_orga_status(user, brand, initiator)

    orga_signals.orga_status_revoked.send(None, event=event)

    flash_success(
        gettext(
            'Organizer status was revoked for %(screen_name)s for brand %(brand_title)s.',
            screen_name=event.user.screen_name,
            brand_title=event.brand.title,
        )
    )


@blueprint.get('/persons/<brand_id>/export')
@permission_required('orga_detail.view')
@textified
def export_persons(brand_id):
    """Export the list of organizers for the brand as a CSV document in
    Microsoft Excel dialect.
    """
    brand = _get_brand_or_404(brand_id)

    field_name_screen_name = gettext('Username')
    field_name_first_name = gettext('First name')
    field_name_last_name = gettext('Last name')
    field_name_date_of_birth = gettext('Date of birth')
    field_name_street = gettext('Street')
    field_name_zip_code = gettext('Zip code')
    field_name_city = gettext('City')
    field_name_country = gettext('Country')
    field_name_email_address = gettext('Email address')
    field_name_phone_number = gettext('Phone number')

    field_names = [
        field_name_screen_name,
        field_name_first_name,
        field_name_last_name,
        field_name_date_of_birth,
        field_name_street,
        field_name_zip_code,
        field_name_city,
        field_name_country,
        field_name_email_address,
        field_name_phone_number,
    ]

    def to_dict(user):
        date_of_birth = (
            user.detail.date_of_birth.strftime('%d.%m.%Y')
            if user.detail.date_of_birth
            else None
        )

        return {
            field_name_screen_name: user.screen_name,
            field_name_first_name: user.detail.first_name,
            field_name_last_name: user.detail.last_name,
            field_name_date_of_birth: date_of_birth,
            field_name_street: user.detail.street,
            field_name_zip_code: user.detail.zip_code,
            field_name_city: user.detail.city,
            field_name_country: user.detail.country,
            field_name_email_address: user.email_address,
            field_name_phone_number: user.detail.phone_number,
        }

    orgas = orga_service.get_orgas_for_brand(brand.id)
    orgas = [orga for orga in orgas if not orga.deleted]
    orgas.sort(key=user_service.get_sort_key_for_screen_name)
    rows = map(to_dict, orgas)
    return serialize_dicts_to_csv(field_names, rows, delimiter=';')


@blueprint.get('/birthdays')
@permission_required('orga_birthday.view')
@templated
def birthdays():
    orgas = list(
        orga_birthday_service.collect_orgas_with_next_birthdays(limit=5)
    )

    return {
        'orgas': orgas,
    }


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand
