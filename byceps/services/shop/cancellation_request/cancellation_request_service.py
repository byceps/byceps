"""
byceps.services.shop.cancellation_request.cancellation_request_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select

from byceps.database import db, paginate, Pagination
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import OrderID
from byceps.services.shop.shop.models import ShopID

from .dbmodels import DbCancellationRequest
from .models import (
    CancellationRequest,
    CancellationRequestQuantitiesByState,
    CancellationRequestState,
    DonationExtent,
)


def create_request_for_full_donation(
    shop_id: ShopID,
    order_id: OrderID,
    order_number: OrderNumber,
    amount_donation: Decimal,
) -> CancellationRequest:
    """Create a cancellation request for the full donation an order."""
    amount_refund = Decimal('0.00')
    recipient_name = None
    recipient_iban = None

    return _create_request(
        shop_id,
        order_id,
        order_number,
        DonationExtent.everything,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )


def create_request_for_partial_refund(
    shop_id: ShopID,
    order_id: OrderID,
    order_number: OrderNumber,
    amount_refund: Decimal,
    amount_donation: Decimal,
    recipient_name: str,
    recipient_iban: str,
) -> CancellationRequest:
    """Create a cancellation request for a partial refund an order."""
    return _create_request(
        shop_id,
        order_id,
        order_number,
        DonationExtent.part,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )


def create_request_for_full_refund(
    shop_id: ShopID,
    order_id: OrderID,
    order_number: OrderNumber,
    amount_refund: Decimal,
    recipient_name: str,
    recipient_iban: str,
) -> CancellationRequest:
    """Create a cancellation request for a full refund an order."""
    amount_donation = Decimal('0.00')

    return _create_request(
        shop_id,
        order_id,
        order_number,
        DonationExtent.nothing,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )


def _create_request(
    shop_id: ShopID,
    order_id: OrderID,
    order_number: OrderNumber,
    donation_extent: DonationExtent,
    amount_refund: Decimal,
    amount_donation: Decimal,
    recipient_name: str | None,
    recipient_iban: str | None,
) -> CancellationRequest:
    """Create a cancellation request for an order."""
    now = datetime.utcnow()

    db_request = DbCancellationRequest(
        now,
        shop_id,
        order_id,
        order_number,
        donation_extent,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )

    db.session.add(db_request)
    db.session.commit()

    return _db_entity_to_request(db_request)


def accept_request(request_id: UUID) -> None:
    """Accept the cancellation request."""
    db_request = db.session.get(DbCancellationRequest, request_id)

    if db_request is None:
        raise ValueError(f'Unknown cancellation request ID "{request_id}"')

    db_request.state = CancellationRequestState.accepted

    db.session.commit()


def get_request(request_id: UUID) -> CancellationRequest | None:
    """Return the cancellation request with that ID."""
    db_request = db.session.get(DbCancellationRequest, request_id)

    if db_request is None:
        return None

    return _db_entity_to_request(db_request)


def get_request_for_order(
    order_id: OrderID,
) -> CancellationRequest | None:
    """Return the cancellation request for that order."""
    db_request = (
        db.session.execute(
            select(DbCancellationRequest).filter_by(order_id=order_id)
        )
        .scalars()
        .one_or_none()
    )

    if db_request is None:
        return None

    return _db_entity_to_request(db_request)


def get_all_requests_for_shop_paginated(
    shop_id: ShopID, page: int, per_page: int
) -> Pagination:
    """Return all cancellation requests for the shop."""
    stmt = (
        select(DbCancellationRequest)
        .filter_by(shop_id=shop_id)
        .order_by(DbCancellationRequest.created_at.desc())
    )

    return paginate(stmt, page, per_page, item_mapper=_db_entity_to_request)


def get_donation_extent_totals_for_shop(
    shop_id: ShopID,
) -> dict[DonationExtent, int]:
    """Return totals per donation extent type for that shop."""
    rows = (
        db.session.execute(
            select(
                DbCancellationRequest._donation_extent,
                db.func.count(DbCancellationRequest._donation_extent),
            )
            .filter_by(shop_id=shop_id)
            .group_by(DbCancellationRequest._donation_extent)
        )
        .tuples()
        .all()
    )

    totals_dict = dict(rows)
    return {
        donation_extent: totals_dict.get(donation_extent.name, 0)
        for donation_extent in DonationExtent
    }


def get_donation_sum_for_shop(shop_id: ShopID) -> Decimal:
    """Return donation total for that shop."""
    return db.session.scalar(
        select(db.func.sum(DbCancellationRequest.amount_donation)).filter_by(
            shop_id=shop_id
        )
    ) or Decimal('0.00')


def get_request_quantities_by_state(
    shop_id: ShopID,
) -> CancellationRequestQuantitiesByState:
    """Return request quantity per state for that shop."""
    rows = (
        db.session.execute(
            select(
                DbCancellationRequest._state,
                db.func.count(DbCancellationRequest._state),
            )
            .filter_by(shop_id=shop_id)
            .group_by(DbCancellationRequest._state)
        )
        .tuples()
        .all()
    )

    quantities_by_state_name = {
        state.name: 0 for state in CancellationRequestState
    }

    for state_name, quantity in rows:
        quantities_by_state_name[state_name] = quantity

    return CancellationRequestQuantitiesByState(
        open=quantities_by_state_name[CancellationRequestState.open.name],
        accepted=quantities_by_state_name[
            CancellationRequestState.accepted.name
        ],
        denied=quantities_by_state_name[CancellationRequestState.denied.name],
        total=sum(quantities_by_state_name.values()),
    )


def _db_entity_to_request(
    db_request: DbCancellationRequest,
) -> CancellationRequest:
    return CancellationRequest(
        id=db_request.id,
        created_at=db_request.created_at,
        shop_id=db_request.shop_id,
        order_id=db_request.order_id,
        order_number=db_request.order_number,
        donation_extent=db_request.donation_extent,
        amount_refund=db_request.amount_refund,
        amount_donation=db_request.amount_donation,
        recipient_name=db_request.recipient_name,
        recipient_iban=db_request.recipient_iban,
        state=db_request.state,
    )
