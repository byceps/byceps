"""
byceps.blueprints.admin.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ....services.brand import service as brand_service
from ....services.user import service as user_service
from ....services.user_badge import awarding_service, badge_service
from ....signals import user_badge as user_badge_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry

from .authorization import UserBadgePermission
from .forms import AwardForm, CreateForm


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

    awarding_counts_by_badge_id = awarding_service.count_awardings()

    badges = [
        {
            'id': badge.id,
            'slug': badge.slug,
            'label': badge.label,
            'image_url_path': badge.image_url_path,
            'brand_title': _find_brand_title(badge.brand_id),
            'featured': badge.featured,
            'awarding_count': awarding_counts_by_badge_id[badge.id],
        }
        for badge in all_badges
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

    awardings = awarding_service.get_awardings_of_badge(badge.id)
    recipient_ids = [awarding.user_id for awarding in awardings]
    recipients = user_service.find_users(recipient_ids, include_avatars=True)
    recipients = list(sorted(recipients, key=lambda r: r.screen_name or ''))

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

    flash_success(f'Das Abzeichen "{badge.label}" wurde angelegt.')
    return redirect_to('.index')


def _set_brand_ids_on_form(form):
    brands = brand_service.get_brands()
    form.set_brand_choices(brands)


@blueprint.route('/awardings/to/<uuid:user_id>')
@permission_required(UserBadgePermission.award)
@templated
def award_form(user_id, erroneous_form=None):
    """Show form to award a badge to a user."""
    user = user_service.find_user(user_id)
    if not user:
        abort(404)

    form = erroneous_form if erroneous_form else AwardForm(user_id=user.id)
    _set_badge_ids_on_form(form)

    return {
        'form': form,
        'user': user,
    }


@blueprint.route('/awardings/to/<uuid:user_id>', methods=['POST'])
@permission_required(UserBadgePermission.award)
def award(user_id):
    """Award a badge to a user."""
    form = AwardForm(request.form)
    _set_badge_ids_on_form(form)

    if not form.validate():
        return award_form(user_id, form)

    badge_id = form.badge_id.data

    user = user_service.find_user(user_id)
    if not user:
        abort(401, 'Unknown user ID')

    badge = badge_service.find_badge(badge_id)
    if not badge:
        abort(401, 'Unknown badge ID')

    initiator_id = g.current_user.id

    _, event = awarding_service.award_badge_to_user(
        badge_id, user_id, initiator_id=initiator_id
    )

    flash_success(
        f'Das Abzeichen "{badge.label}" wurde an {user.screen_name} verliehen.'
    )

    user_badge_signals.user_badge_awarded.send(None, event=event)

    return redirect_to('user_admin.view', user_id=user.id)


def _set_badge_ids_on_form(form):
    badges = badge_service.get_all_badges()
    form.set_badge_choices(badges)
