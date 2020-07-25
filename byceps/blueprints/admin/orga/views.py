"""
byceps.blueprints.admin.orga.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from flask import abort, g, request

from ....services.brand import service as brand_service
from ....services.orga import service as orga_service
from ....services.orga import birthday_service as orga_birthday_service
from ....services.user import service as user_service
from ....util.export import serialize_to_csv
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to, respond_no_content, textified

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from ..orga_team.authorization import OrgaTeamPermission

from .authorization import OrgaBirthdayPermission, OrgaDetailPermission
from .forms import OrgaFlagCreateForm


blueprint = create_blueprint('orga_admin', __name__)


permission_registry.register_enum(OrgaBirthdayPermission)
permission_registry.register_enum(OrgaDetailPermission)
permission_registry.register_enum(OrgaTeamPermission)


@blueprint.route('/persons')
@permission_required(OrgaDetailPermission.view)
@templated
def persons():
    """List brands to choose from."""
    brands_with_person_counts = orga_service.get_brands_with_person_counts()

    return {
        'brands_with_person_counts': brands_with_person_counts,
    }


@blueprint.route('/persons/<brand_id>')
@permission_required(OrgaDetailPermission.view)
@templated
def persons_for_brand(brand_id):
    """List organizers for the brand with details."""
    brand = _get_brand_or_404(brand_id)

    orgas = orga_service.get_orgas_for_brand(brand.id)
    orgas.sort(key=user_service.get_sort_key_for_screen_name)

    return {
        'brand': brand,
        'orgas': orgas,
    }


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
    initiator = g.current_user

    orga_flag = orga_service.add_orga_flag(brand.id, user.id, initiator.id)

    flash_success(
        f'{orga_flag.user.screen_name} wurde das Orga-Flag '
        f'für die Marke {orga_flag.brand.title} gegeben.'
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
    initiator = g.current_user

    orga_service.remove_orga_flag(orga_flag, initiator.id)

    flash_success(
        f'{user.screen_name} wurde das Orga-Flag '
        f'für die Marke {brand.title} entzogen.'
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
