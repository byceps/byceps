"""
byceps.services.shop.payment.payment_gateway_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.shop.storefront.models import StorefrontID
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbPaymentGateway, DbStorefrontPaymentGateway
from .models import PaymentGateway


def create_payment_gateway(
    payment_gateway_id: str, name: str, enabled: bool
) -> PaymentGateway:
    """Create a payment gateway."""
    db_payment_gateway = DbPaymentGateway(payment_gateway_id, name, enabled)
    db.session.add(db_payment_gateway)
    db.session.commit()

    return _db_entity_to_payment_gateway(db_payment_gateway)


def update_payment_gateway(
    payment_gateway_id: str, name: str, enabled: bool
) -> Result[PaymentGateway, str]:
    """Update a payment gateway."""
    db_payment_gateway_result = _get_db_payment_gateway(payment_gateway_id)
    if db_payment_gateway_result.is_err():
        return Err(db_payment_gateway_result.unwrap_err())

    db_payment_gateway = db_payment_gateway_result.unwrap()

    db_payment_gateway.id = payment_gateway_id
    db_payment_gateway.name = name
    db_payment_gateway.enabled = enabled

    db.session.commit()

    return Ok(_db_entity_to_payment_gateway(db_payment_gateway))


def delete_payment_gateway(payment_gateway_id: str) -> None:
    """Delete a payment gateway."""
    db.session.execute(
        delete(DbPaymentGateway).where(
            DbPaymentGateway.id == payment_gateway_id
        )
    )
    db.session.commit()


def find_payment_gateway(payment_gateway_id: str) -> PaymentGateway | None:
    """Return the payment gateway with that id, or `None` if not found."""
    db_payment_gateway = _find_db_payment_gateway(payment_gateway_id)

    if db_payment_gateway is None:
        return None

    return _db_entity_to_payment_gateway(db_payment_gateway)


def _find_db_payment_gateway(
    payment_gateway_id: str,
) -> DbPaymentGateway | None:
    """Return the database entity for the payment gateway with that id, or `None`
    if not found.
    """
    return db.session.get(DbPaymentGateway, payment_gateway_id)


def get_payment_gateway(payment_gateway_id: str) -> Result[PaymentGateway, str]:
    """Return the payment gateway with that id, or raise an exception."""
    payment_gateway = find_payment_gateway(payment_gateway_id)

    if payment_gateway is None:
        return Err(f'Unknown payment gateway ID "{payment_gateway_id}"')

    return Ok(payment_gateway)


def _get_db_payment_gateway(
    payment_gateway_id: str,
) -> Result[DbPaymentGateway, str]:
    """Return the database entity for the payment gateway with that id.

    Raise an exception if not found.
    """
    db_payment_gateway = _find_db_payment_gateway(payment_gateway_id)

    if db_payment_gateway is None:
        return Err(f'Unknown payment gateway ID "{payment_gateway_id}"')

    return Ok(db_payment_gateway)


def get_all_payment_gateways() -> list[PaymentGateway]:
    """Return all payment gateways."""
    db_payment_gateways = db.session.scalars(select(DbPaymentGateway)).all()

    return [
        _db_entity_to_payment_gateway(db_payment_gateway)
        for db_payment_gateway in db_payment_gateways
    ]


def get_enabled_payment_gateways() -> list[PaymentGateway]:
    """Return all enabled payment gateways."""
    db_payment_gateways = db.session.scalars(
        select(DbPaymentGateway).filter_by(enabled=True)
    ).all()

    return [
        _db_entity_to_payment_gateway(db_payment_gateway)
        for db_payment_gateway in db_payment_gateways
    ]


def _db_entity_to_payment_gateway(
    db_payment_gateway: DbPaymentGateway,
) -> PaymentGateway:
    return PaymentGateway(
        id=db_payment_gateway.id,
        name=db_payment_gateway.name,
        enabled=db_payment_gateway.enabled,
    )


def enable_payment_gateway_for_storefront(
    payment_gateway_id: str,
    storefront_id: StorefrontID,
) -> Result[None, str]:
    get_payment_gateway_result = get_payment_gateway(payment_gateway_id)
    if get_payment_gateway_result.is_err():
        return Err(get_payment_gateway_result.unwrap_err())

    db_storefront_payment_gateway = DbStorefrontPaymentGateway(
        storefront_id, payment_gateway_id
    )
    db.session.add(db_storefront_payment_gateway)
    db.session.commit()

    return Ok(None)


def get_payment_gateways_enabled_for_storefront(
    storefront_id: StorefrontID,
) -> list[PaymentGateway]:
    """Return the payment gateways that are enabled for the storefront.

    To be included, a payment gateway must be enabled and assigned to
    the storefront.
    """
    db_payment_gateways = db.session.scalars(
        select(DbPaymentGateway)
        .join(DbStorefrontPaymentGateway)
        .filter(DbPaymentGateway.enabled == True)  # noqa: E712
        .filter(DbStorefrontPaymentGateway.storefront_id == storefront_id)
    ).all()

    return [
        _db_entity_to_payment_gateway(db_payment_gateway)
        for db_payment_gateway in db_payment_gateways
    ]


def is_payment_gateway_enabled_for_storefront(
    payment_gateway_id: str,
    storefront_id: StorefrontID,
) -> bool:
    """Return `True` if the payment gateway is enabled for the storefront.

    That is the case if:
    - a payment gateway with that ID exists and
    - the payment gateway is enabled and
    - the payment gateway is assigned to the storefront.
    """
    stmt = select(
        select(DbStorefrontPaymentGateway)
        .join(DbPaymentGateway)
        .filter(DbPaymentGateway.id == payment_gateway_id)
        .filter(DbPaymentGateway.enabled == True)  # noqa: E712
        .filter(DbStorefrontPaymentGateway.storefront_id == storefront_id)
        .exists()
    )

    return db.session.scalar(stmt) or False
