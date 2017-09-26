"""
byceps.blueprints.user_badge_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ...services.brand import service as brand_service
from ...services.user import service as user_service
from ...services.user_badge import service as badge_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated


blueprint = create_blueprint('user_badge_admin', __name__)


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
    recipients = user_service.find_users(recipient_ids)

    return {
        'badge': badge,
        'recipients': recipients,
    }
