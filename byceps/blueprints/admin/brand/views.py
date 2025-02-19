"""
byceps.blueprints.admin.brand.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext
from moneyed import get_currency

from byceps.services.brand import brand_service, brand_setting_service
from byceps.services.email import email_config_service, email_footer_service
from byceps.services.orga import orga_service
from byceps.services.party import party_service
from byceps.services.shop.order import order_payment_service
from byceps.services.shop.shop import shop_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.l10n import get_default_locale, get_locale_str
from byceps.util.views import permission_required, redirect_to

from .forms import CreateForm, EmailConfigUpdateForm, UpdateForm


blueprint = create_blueprint('brand_admin', __name__)


@blueprint.get('/')
@permission_required('brand.view')
@templated
def index():
    """List brands."""
    brands = brand_service.get_all_brands()

    party_count_by_brand_id = party_service.get_party_count_by_brand_id()

    orga_count_by_brand_id = orga_service.get_person_count_by_brand_id()

    return {
        'brands': brands,
        'party_count_by_brand_id': party_count_by_brand_id,
        'orga_count_by_brand_id': orga_count_by_brand_id,
    }


@blueprint.get('/brands/<brand_id>')
@permission_required('brand.view')
@templated
def view(brand_id):
    """Show a brand."""
    brand = _get_brand_or_404(brand_id)

    current_party = brand_service.find_current_party(brand.id)
    settings = brand_setting_service.get_settings(brand.id)
    email_config = email_config_service.get_config(brand.id)

    return {
        'brand': brand,
        'current_party': current_party,
        'settings': settings,
        'email_config': email_config,
    }


@blueprint.get('/create')
@permission_required('brand.create')
@templated
def create_form(erroneous_form=None):
    """Show form to create a brand."""
    locale = get_locale_str() or get_default_locale()

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_currency_choices(locale)

    return {
        'form': form,
    }


@blueprint.post('/')
@permission_required('brand.create')
def create():
    """Create a brand."""
    locale = get_default_locale()

    form = CreateForm(request.form)
    form.set_currency_choices(locale)

    if not form.validate():
        return create_form(form)

    brand_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    currency = get_currency(form.currency.data)

    brand = brand_service.create_brand(brand_id, title)

    sender_address = f'noreply@{brand.id}.example'
    contact_address = f'info@{brand.id}.example'

    email_footer_service.create_footers(brand, g.user, contact_address)

    email_config_service.create_config(
        brand.id,
        sender_address=sender_address,
        sender_name=brand.title,
        contact_address=contact_address,
    )

    shop = shop_service.create_shop(brand, currency)

    order_payment_service.create_email_payment_instructions(shop.id, g.user)
    order_payment_service.create_html_payment_instructions(shop.id, g.user)

    flash_success(
        gettext('Brand "%(title)s" has been created.', title=brand.title)
    )
    return redirect_to('.view', brand_id=brand.id)


@blueprint.get('/brands/<brand_id>/update')
@permission_required('brand.update')
@templated
def update_form(brand_id, erroneous_form=None):
    """Show form to update a brand."""
    brand = _get_brand_or_404(brand_id)

    current_party = brand_service.find_current_party(brand.id)
    current_party_id = current_party.id if current_party else None

    form = (
        erroneous_form
        if erroneous_form
        else UpdateForm(
            brand.title, obj=brand, current_party_id=current_party_id
        )
    )
    form.set_current_party_id_choices(brand.id)

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/brands/<brand_id>')
@permission_required('brand.update')
def update(brand_id):
    """Update a brand."""
    brand = _get_brand_or_404(brand_id)

    form = UpdateForm(brand.title, request.form)
    form.set_current_party_id_choices(brand.id)
    if not form.validate():
        return update_form(brand.id, form)

    title = form.title.data.strip()
    image_filename = form.image_filename.data.strip() or None
    current_party_id = form.current_party_id.data
    archived = form.archived.data

    brand = brand_service.update_brand(
        brand.id, title, image_filename, archived
    )

    if current_party_id:
        brand_service.set_current_party(brand.id, current_party_id)
    else:
        brand_service.unset_current_party(brand.id)

    flash_success(
        gettext('Brand "%(title)s" has been updated.', title=brand.title)
    )
    return redirect_to('.view', brand_id=brand.id)


# -------------------------------------------------------------------- #
# email config


@blueprint.get('/brands/<brand_id>/email_config/update')
@permission_required('brand.update')
@templated
def email_config_update_form(brand_id, erroneous_form=None):
    """Show form to update e-mail config."""
    brand = _get_brand_or_404(brand_id)

    config = email_config_service.get_config(brand.id)

    form = (
        erroneous_form
        if erroneous_form
        else EmailConfigUpdateForm(
            sender_address=config.sender.address,
            sender_name=config.sender.name,
            contact_address=config.contact_address,
        )
    )

    return {
        'brand': brand,
        'config': config,
        'form': form,
    }


@blueprint.post('/brands/<brand_id>/email_config')
@permission_required('brand.update')
def email_config_update(brand_id):
    """Update e-mail config."""
    brand = _get_brand_or_404(brand_id)

    config = email_config_service.get_config(brand.id)

    form = EmailConfigUpdateForm(request.form)
    if not form.validate():
        return email_config_update_form(brand.id, form)

    sender_address = form.sender_address.data.strip()
    sender_name = form.sender_name.data.strip()
    contact_address = form.contact_address.data.strip()

    update_result = email_config_service.update_config(
        config.brand_id, sender_address, sender_name, contact_address
    )

    if update_result.is_err():
        flash_error(update_result.unwrap_err())
    else:
        flash_success(gettext('Email configuration has been updated.'))

    return redirect_to('.view', brand_id=brand.id)


# -------------------------------------------------------------------- #
# helpers


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand
