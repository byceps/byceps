"""
byceps.services.shop.cancelation_request.cancelation_request_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select

from ....database import db, paginate, Pagination

from ..order.dbmodels.order import DbOrder
from ..order.models.number import OrderNumber
from ..shop.models import ShopID

from .dbmodels import DbCancelationRequest
from .models import (
    CancelationRequest,
    CancelationRequestQuantitiesByState,
    CancelationRequestState,
    DonationExtent,
)


def create_request_for_full_donation(
    shop_id: ShopID,
    order_number: OrderNumber,
    amount_donation: Decimal,
) -> CancelationRequest:
    """Create a cancelation request for the full donation an order."""
    amount_refund = Decimal('0.00')
    recipient_name = None
    recipient_iban = None

    return _create_request(
        shop_id,
        order_number,
        DonationExtent.everything,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )


def create_request_for_partial_refund(
    shop_id: ShopID,
    order_number: OrderNumber,
    amount_refund: Decimal,
    amount_donation: Decimal,
    recipient_name: str,
    recipient_iban: str,
) -> CancelationRequest:
    """Create a cancelation request for a partial refund an order."""
    return _create_request(
        shop_id,
        order_number,
        DonationExtent.part,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )


def create_request_for_full_refund(
    shop_id: ShopID,
    order_number: OrderNumber,
    amount_refund: Decimal,
    recipient_name: str,
    recipient_iban: str,
) -> CancelationRequest:
    """Create a cancelation request for a full refund an order."""
    amount_donation = Decimal('0.00')

    return _create_request(
        shop_id,
        order_number,
        DonationExtent.nothing,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )


def _create_request(
    shop_id: ShopID,
    order_number: OrderNumber,
    donation_extent: DonationExtent,
    amount_refund: Decimal,
    amount_donation: Decimal,
    recipient_name: Optional[str],
    recipient_iban: Optional[str],
) -> CancelationRequest:
    """Create a cancelation request for an order."""
    now = datetime.utcnow()

    db_request = DbCancelationRequest(
        now,
        shop_id,
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
    """Accept the cancelation request."""
    db_request = db.session.get(DbCancelationRequest, request_id)

    if db_request is None:
        raise ValueError(f'Unknown cancelation request ID "{request_id}"')

    db_request.state = CancelationRequestState.accepted

    db.session.commit()


def get_request(request_id: UUID) -> Optional[CancelationRequest]:
    """Return the cancelation request with that ID."""
    db_request = db.session.get(DbCancelationRequest, request_id)

    if db_request is None:
        return None

    return _db_entity_to_request(db_request)


def get_request_for_order_number(
    order_number: OrderNumber,
) -> Optional[CancelationRequest]:
    """Return the cancelation request for that order number."""
    db_request = (
        db.session.execute(
            select(DbCancelationRequest)
            .join(DbOrder)
            .filter(DbOrder.order_number == order_number)
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
    """Return all cancelation requests for the shop."""
    stmt = (
        select(DbCancelationRequest)
        .filter_by(shop_id=shop_id)
        .order_by(DbCancelationRequest.created_at.desc())
    )

    return paginate(stmt, page, per_page, item_mapper=_db_entity_to_request)


def get_donation_extent_totals_for_shop(
    shop_id: ShopID,
) -> dict[DonationExtent, int]:
    """Return totals per donation extent type for that shop."""
    rows = (
        db.session.execute(
            select(
                DbCancelationRequest._donation_extent,
                db.func.count(DbCancelationRequest._donation_extent),
            )
            .filter_by(shop_id=shop_id)
            .group_by(DbCancelationRequest._donation_extent)
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
    return db.session.execute(
        select(db.func.sum(DbCancelationRequest.amount_donation)).filter_by(
            shop_id=shop_id
        )
    ).scalar()


def get_request_quantities_by_state(
    shop_id: ShopID,
) -> CancelationRequestQuantitiesByState:
    """Return request quantity per state for that shop."""
    rows = (
        db.session.execute(
            select(
                DbCancelationRequest._state,
                db.func.count(DbCancelationRequest._state),
            )
            .filter_by(shop_id=shop_id)
            .group_by(DbCancelationRequest._state)
        )
        .tuples()
        .all()
    )

    quantities_by_state_name = {
        state.name: 0 for state in CancelationRequestState
    }

    for state_name, quantity in rows:
        quantities_by_state_name[state_name] = quantity

    return CancelationRequestQuantitiesByState(
        open=quantities_by_state_name[CancelationRequestState.open.name],
        accepted=quantities_by_state_name[
            CancelationRequestState.accepted.name
        ],
        denied=quantities_by_state_name[CancelationRequestState.denied.name],
        total=sum(quantities_by_state_name.values()),
    )


def _db_entity_to_request(
    db_request: DbCancelationRequest,
) -> CancelationRequest:
    return CancelationRequest(
        id=db_request.id,
        created_at=db_request.created_at,
        shop_id=db_request.shop_id,
        order_number=db_request.order_number,
        donation_extent=db_request.donation_extent,
        amount_refund=db_request.amount_refund,
        amount_donation=db_request.amount_donation,
        recipient_name=db_request.recipient_name,
        recipient_iban=db_request.recipient_iban,
        state=db_request.state,
    )
