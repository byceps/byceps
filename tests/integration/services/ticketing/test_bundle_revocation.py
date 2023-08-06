"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.ticketing import (
    ticket_bundle_service as bundle_service,
    ticket_log_service,
    ticket_service,
)


def test_revoke_bundle(admin_app, bundle, ticketing_admin):
    expected_quantity = 4

    tickets_before = bundle_service.get_tickets_for_bundle(bundle.id)
    assert len(tickets_before) == expected_quantity

    for ticket_before in tickets_before:
        assert not ticket_before.revoked

        log_entries_before = ticket_log_service.get_entries_for_ticket(
            ticket_before.id
        )
        assert len(log_entries_before) == 0

    # -------------------------------- #

    bundle_service.revoke_bundle(bundle.id, ticketing_admin)

    # -------------------------------- #

    tickets_after = bundle_service.get_tickets_for_bundle(bundle.id)
    assert len(tickets_after) == expected_quantity

    for ticket_after in tickets_after:
        assert ticket_after.revoked

        log_entries_after = ticket_log_service.get_entries_for_ticket(
            ticket_after.id
        )
        assert len(log_entries_after) == 1

        ticket_revoked_log_entry = log_entries_after[0]
        assert ticket_revoked_log_entry.event_type == 'ticket-revoked'
        assert ticket_revoked_log_entry.data == {
            'initiator_id': str(ticketing_admin.id),
        }


# helpers


@pytest.fixture()
def bundle(category, ticket_owner):
    quantity = 4
    bundle = bundle_service.create_bundle(
        category.party_id, category.id, quantity, ticket_owner
    )

    yield bundle

    for ticket in bundle.tickets:
        ticket_service.delete_ticket(ticket.id)
    bundle_service.delete_bundle(bundle.id)
