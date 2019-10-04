"""
byceps.blueprints.admin.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.brand import service as brand_service
from ....services.user import service as user_service
from ....services.user_badge import service as badge_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import UserBadgePermission
from .forms import CreateForm


blueprint = create_blueprint('user_badge_admin', __name__)


permission_registry.register_enum(UserBadgePermission)


@blueprint.route('/badges')
@templated
def index():
    """List all badges."""
    all_badges = badge_service.get_all_badges()

    brands = brand_service.get_brands()
    brands_by_id = {brand.id: brand for brand in brands}

    def _find_brand_title(brand_id):
        if brand_id is None:
            return None

        return brands_by_id[brand_id].title

    badges = [
        {
            'id': badge.id,
            'slug': badge.slug,
            'label': badge.label,
            'image_url': badge.image_url,
            'brand_title': _find_brand_title(badge.brand_id),
            'featured': badge.featured,
        } for badge in all_badges
    ]

    return {
        'badges': badges,
    }


@blueprint.route('/badges/<uuid:badge_id>')
@templated
def view(badge_id):
    """Show badge details."""
    badge = badge_service.find_badge(badge_id)

    if badge is None:
        abort(404)

    awardings = badge_service.get_awardings_of_badge(badge.id)
    recipient_ids = [awarding.user_id for awarding in awardings]
    recipients = user_service.find_users(recipient_ids, include_avatars=True)

    return {
        'badge': badge,
        'recipients': recipients,
    }


@blueprint.route('/create')
@permission_required(UserBadgePermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create a user badge."""
    form = erroneous_form if erroneous_form else CreateForm()
    _set_brand_ids_on_form(form)

    return {
        'form': form,
    }


@blueprint.route('/badges', methods=['POST'])
@permission_required(UserBadgePermission.create)
def create():
    """Create a user badge."""
    form = CreateForm(request.form)
    _set_brand_ids_on_form(form)

    if not form.validate():
        return create_form(form)

    brand_id = form.brand_id.data
    slug = form.slug.data.strip()
    label = form.label.data.strip()
    description = form.description.data.strip()
    image_filename = form.image_filename.data.strip()
    featured = form.featured.data

    if brand_id:
        brand = brand_service.find_brand(brand_id)
        brand_id = brand.id
    else:
        brand_id = None

    badge = badge_service.create_badge(
        slug,
        label,
        image_filename,
        brand_id=brand_id,
        description=description,
        featured=featured,
    )

    flash_success('Das Abzeichen "{}" wurde angelegt.', badge.label)
    return redirect_to('.index')


def _set_brand_ids_on_form(form):
    brands = brand_service.get_brands()
    form.set_brand_choices(brands)
