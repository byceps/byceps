"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)
from byceps.services.user_badge.models import QuantifiedBadgeAwarding


def test_award_badge(api_client, api_client_authz_header, user, admin_user):
    badge = user_badge_service.create_badge(
        'supporter', 'Supporter', 'supporter.svg'
    )

    before = user_badge_awarding_service.get_awardings_of_badge(badge.id)
    assert before == set()

    url = 'http://api.acmecon.test/v1/user_badges/awardings'
    headers = [api_client_authz_header]
    json_data = {
        'badge_slug': 'supporter',
        'awardee_id': str(user.id),
        'initiator_id': str(admin_user.id),
    }

    response = api_client.post(url, headers=headers, json=json_data)
    assert response.status_code == 204

    actual = user_badge_awarding_service.get_awardings_of_badge(badge.id)
    assert actual == {
        QuantifiedBadgeAwarding(
            badge_id=badge.id,
            awardee_id=user.id,
            quantity=1,
        )
    }
