"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.ticketing import (
    category_service,
    event_service,
    ticket_bundle_service as bundle_service,
)

from tests.helpers import create_brand, create_party


def test_revoke_bundle(admin_app_with_db, normal_user, admin_user):
    brand = create_brand()
    party = create_party(brand_id=brand.id)

    quantity = 4
    owner = normal_user

    bundle = create_bundle(party.id, quantity, owner)

    tickets_before = bundle_service.find_tickets_for_bundle(bundle.id)
    assert len(tickets_before) == quantity

    for ticket_before in tickets_before:
        assert not ticket_before.revoked

        events_before = event_service.get_events_for_ticket(ticket_before.id)
        assert len(events_before) == 0

    # -------------------------------- #

    bundle_service.revoke_bundle(bundle.id, admin_user.id)

    # -------------------------------- #

    tickets_after = bundle_service.find_tickets_for_bundle(bundle.id)
    assert len(tickets_after) == quantity

    for ticket_after in tickets_after:
        assert ticket_after.revoked

        events_after = event_service.get_events_for_ticket(ticket_after.id)
        assert len(events_after) == 1

        ticket_revoked_event = events_after[0]
        assert ticket_revoked_event.event_type == 'ticket-revoked'
        assert ticket_revoked_event.data == {
            'initiator_id': str(admin_user.id),
        }


# helpers


def create_bundle(party_id, quantity, owner):
    category = create_category(party_id, 'Premium')

    return bundle_service.create_bundle(category.id, quantity, owner.id)


def create_category(party_id, title):
    return category_service.create_category(party_id, title)
