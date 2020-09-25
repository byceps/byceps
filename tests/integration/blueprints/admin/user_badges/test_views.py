"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.user_badge import badge_service

from tests.helpers import http_client


def test_index(admin_app, user_badge_admin, ):
    url = '/admin/user_badges/badges'
    response = get_resource(admin_app, user_badge_admin, url)
    assert response.status_code == 200


def test_view(admin_app, user_badge_admin, badge):
    url = f'/admin/user_badges/badges/{badge.id}'
    response = get_resource(admin_app, user_badge_admin, url)
    assert response.status_code == 200


def test_create_form(admin_app, user_badge_admin):
    url = '/admin/user_badges/create'
    response = get_resource(admin_app, user_badge_admin, url)
    assert response.status_code == 200


def test_create(admin_app, user_badge_admin, brand):
    slug = 'seal-of-resilience'
    label = 'Seal of Resilience'
    image_filename = 'seal-of-resilience.svg'
    description = 'Stay put, get this.'

    assert badge_service.find_badge_by_slug(slug) is None

    url = f'/admin/user_badges/badges'
    form_data = {
        'slug': slug,
        'label': label,
        'image_filename': image_filename,
        'description': description,
        'brand_id': brand.id,
        'featured': 'Y',
    }
    response = post_resource(admin_app, user_badge_admin, url, form_data)

    badge = badge_service.find_badge_by_slug(slug)
    assert badge is not None
    assert badge.id is not None
    assert badge.slug == slug
    assert badge.label == label
    assert badge.image_filename == image_filename
    assert badge.description == description
    assert badge.brand_id == brand.id
    assert badge.featured

    # Clean up.
    badge_service.delete_badge(badge.id)


def test_update_form(admin_app, user_badge_admin, badge):
    url = f'/admin/user_badges/badges/{badge.id}/update'
    response = get_resource(admin_app, user_badge_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)


def post_resource(app, user, url, data):
    with http_client(app, user_id=user.id) as client:
        return client.post(url, data=data)
