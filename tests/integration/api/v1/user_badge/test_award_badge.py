"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user_badge import awarding_service, badge_service
from byceps.services.user_badge.transfer.models import QuantifiedBadgeAwarding


def test_award_badge(api_client, api_client_authz_header, user, admin_user):
    badge = badge_service.create_badge(
        'supporter', 'Supporter', 'supporter.svg'
    )

    before = awarding_service.get_awardings_of_badge(badge.id)
    assert before == set()

    url = f'/api/v1/user_badges/awardings'
    headers = [api_client_authz_header]
    json_data = {
        'badge_slug': 'supporter',
        'user_id': str(user.id),
        'initiator_id': str(admin_user.id),
    }

    response = api_client.post(url, headers=headers, json=json_data)
    assert response.status_code == 204

    actual = awarding_service.get_awardings_of_badge(badge.id)
    assert actual == {QuantifiedBadgeAwarding(badge.id, user.id, 1)}
