"""
byceps.blueprints.admin.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask import abort, g, request
from flask_babel import gettext

from ....services.brand import service as brand_service
from ....services.orga import birthday_service as orga_birthday_service
from ....services.orga import service as orga_service
from ....services.orga.transfer.models import Birthday
from ....services.user import service as user_service
from ....util.export import serialize_to_csv
from ....util.authorization import register_permission_enum
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
    textified,
)

from ..orga_team.authorization import OrgaTeamPermission

from .authorization import OrgaBirthdayPermission, OrgaDetailPermission
from .forms import OrgaFlagCreateForm


blueprint = create_blueprint('orga_admin', __name__)


register_permission_enum(OrgaBirthdayPermission)
register_permission_enum(OrgaDetailPermission)
register_permission_enum(OrgaTeamPermission)


@blueprint.route('/persons/<brand_id>')
@permission_required(OrgaDetailPermission.view)
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


def _to_birthday(user) -> Optional[Birthday]:
    dob = user.detail.date_of_birth

    if dob is None:
        return None

    return Birthday(dob)


@blueprint.route('/persons/<brand_id>/create')
@permission_required(OrgaTeamPermission.administrate_memberships)
@templated
def create_orgaflag_form(brand_id, erroneous_form=None):
    """Show form to give the organizer flag to a user."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else OrgaFlagCreateForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/persons/<brand_id>', methods=['POST'])
@permission_required(OrgaTeamPermission.administrate_memberships)
def create_orgaflag(brand_id):
    """Give the organizer flag to a user."""
    brand = _get_brand_or_404(brand_id)

    form = OrgaFlagCreateForm(request.form, brand_id=brand.id)
    if not form.validate():
        return create_orgaflag_form(brand.id, form)

    user = form.user.data
    initiator = g.user

    orga_flag = orga_service.add_orga_flag(brand.id, user.id, initiator.id)

    flash_success(
        gettext(
            '%(screen_name)s has received the orga flag '
            'for brand %(brand_title)s.',
            screen_name=orga_flag.user.screen_name,
            brand_title=orga_flag.brand.title,
        )
    )
    return redirect_to('.persons_for_brand', brand_id=orga_flag.brand.id)


@blueprint.route('/persons/<brand_id>/<uuid:user_id>', methods=['DELETE'])
@permission_required(OrgaTeamPermission.administrate_memberships)
@respond_no_content
def remove_orgaflag(brand_id, user_id):
    """Remove the organizer flag for a brand from a person."""
    orga_flag = orga_service.find_orga_flag(brand_id, user_id)

    if orga_flag is None:
        abort(404)

    brand = orga_flag.brand
    user = orga_flag.user
    initiator = g.user

    orga_service.remove_orga_flag(orga_flag, initiator.id)

    flash_success(
        gettext(
            '%(screen_name)s has lost the orga flag '
            'for brand %(brand_title)s.',
            screen_name=user.screen_name,
            brand_title=brand.title,
        )
    )


@blueprint.route('/persons/<brand_id>/export')
@permission_required(OrgaDetailPermission.view)
@textified
def export_persons(brand_id):
    """Export the list of organizers for the brand as a CSV document in
    Microsoft Excel dialect.
    """
    brand = _get_brand_or_404(brand_id)

    field_names = [
        'Benutzername',
        'Vorname',
        'Nachname',
        'Geburtstag',
        'Straße',
        'PLZ',
        'Ort',
        'Land',
        'E-Mail-Adresse',
        'Telefonnummer',
    ]

    def to_dict(user):
        date_of_birth = (
            user.detail.date_of_birth.strftime('%d.%m.%Y')
            if user.detail.date_of_birth
            else None
        )

        return {
            'Benutzername': user.screen_name,
            'Vorname': user.detail.first_names,
            'Nachname': user.detail.last_name,
            'Geburtstag': date_of_birth,
            'Straße': user.detail.street,
            'PLZ': user.detail.zip_code,
            'Ort': user.detail.city,
            'Land': user.detail.country,
            'E-Mail-Adresse': user.email_address,
            'Telefonnummer': user.detail.phone_number,
        }

    orgas = orga_service.get_orgas_for_brand(brand.id)
    orgas = [orga for orga in orgas if not orga.deleted]
    orgas.sort(key=user_service.get_sort_key_for_screen_name)
    rows = map(to_dict, orgas)
    return serialize_to_csv(field_names, rows)


@blueprint.route('/birthdays')
@permission_required(OrgaBirthdayPermission.view)
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
