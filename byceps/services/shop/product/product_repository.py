"""
byceps.services.shop.product.product_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.sql import Select

from byceps.database import db, paginate, Pagination
from byceps.services.shop.order.dbmodels.line_item import DbLineItem
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.order import PaymentState
from byceps.services.shop.shop.models import ShopID
from byceps.util.uuid import generate_uuid7

from .dbmodels.product import DbProduct, DbProductImage
from .dbmodels.attached_product import DbAttachedProduct
from .models import (
    Product,
    ProductID,
    ProductImage,
    ProductNumber,
    AttachedProductID,
)


class UnknownProductIdError(ValueError):
    pass


def create_product(product: Product) -> None:
    """Create a product."""
    db_product = DbProduct(
        product.id,
        product.shop_id,
        product.item_number,
        product.type_,
        product.name,
        product.price,
        product.tax_rate,
        product.total_quantity,
        product.quantity,
        product.max_quantity_per_order,
        product.processing_required,
        type_params=product.type_params,
        available_from=product.available_from,
        available_until=product.available_until,
        not_directly_orderable=product.not_directly_orderable,
        separate_order_required=product.separate_order_required,
    )

    db.session.add(db_product)
    db.session.commit()


def update_product(product: Product) -> None:
    """Update the product."""
    db_product = _get_db_product(product.id)

    db_product.name = product.name
    db_product.price_amount = product.price.amount
    db_product.price_currency = product.price.currency
    db_product.tax_rate = product.tax_rate
    db_product.available_from = product.available_from
    db_product.available_until = product.available_until
    db_product.total_quantity = product.total_quantity
    db_product.max_quantity_per_order = product.max_quantity_per_order
    db_product.not_directly_orderable = product.not_directly_orderable
    db_product.separate_order_required = product.separate_order_required
    db_product.archived = product.archived

    db.session.commit()


def create_product_image(image: ProductImage) -> None:
    """Create an image for a product."""
    # Verify if product exists.
    _get_db_product(image.product_id)

    db_image = DbProductImage(
        image.id,
        image.product_id,
        image.url,
        image.url_preview,
        image.position,
    )
    db.session.add(db_image)
    db.session.commit()


def attach_product(
    product_id_to_attach: ProductID,
    quantity: int,
    product_id_to_attach_to: ProductID,
) -> None:
    """Attach a product to another product."""
    attached_product_id = AttachedProductID(generate_uuid7())

    db_attached_product = DbAttachedProduct(
        attached_product_id,
        product_id_to_attach,
        quantity,
        product_id_to_attach_to,
    )

    db.session.add(db_attached_product)
    db.session.commit()


def unattach_product(attached_product_id: AttachedProductID) -> None:
    """Unattach a product from another."""
    db.session.execute(
        delete(DbAttachedProduct).filter_by(id=attached_product_id)
    )
    db.session.commit()


def increase_quantity(
    product_id: ProductID, quantity_to_increase_by: int, commit: bool
) -> None:
    """Increase product quantity by the given value."""
    db.session.execute(
        update(DbProduct)
        .where(DbProduct.id == product_id)
        .values(quantity=DbProduct.quantity + quantity_to_increase_by)
    )

    if commit:
        db.session.commit()


def decrease_quantity(
    product_id: ProductID, quantity_to_decrease_by: int, commit: bool
) -> None:
    """Decrease product quantity by the given value."""
    db.session.execute(
        update(DbProduct)
        .where(DbProduct.id == product_id)
        .values(quantity=DbProduct.quantity - quantity_to_decrease_by)
    )

    if commit:
        db.session.commit()


def delete_product(product_id: ProductID) -> None:
    """Delete a product."""
    db.session.execute(delete(DbProduct).filter_by(id=product_id))
    db.session.commit()


def find_product(product_id: ProductID) -> DbProduct | None:
    """Return the product with that ID, or `None` if not found."""
    return find_db_product(product_id)


def find_db_product(product_id: ProductID) -> DbProduct | None:
    """Return the database entity for the product with that ID, or
    `None` if not found.
    """
    return db.session.get(DbProduct, product_id)


def _get_db_product(product_id: ProductID) -> DbProduct:
    """Return the database entity for the product with that ID.

    Raise an exception if not found.
    """
    db_product = find_db_product(product_id)

    if db_product is None:
        raise UnknownProductIdError(product_id)

    return db_product


def find_product_with_details(product_id: ProductID) -> DbProduct | None:
    """Return the product with that ID, or `None` if not found."""
    return (
        db.session.execute(
            select(DbProduct)
            .options(
                db.joinedload(DbProduct.products_attached_to).joinedload(
                    DbAttachedProduct.product
                ),
                db.joinedload(DbProduct.attached_products).joinedload(
                    DbAttachedProduct.product
                ),
            )
            .filter_by(id=product_id)
        )
        .unique()
        .scalar_one_or_none()
    )


def is_name_available(shop_id: ShopID, name: str) -> bool:
    """Check if the name is yet unused."""
    return not db.session.scalar(
        select(
            db.exists()
            .where(DbProduct.shop_id == shop_id)
            .where(db.func.lower(DbProduct.name) == name.lower())
        )
    )


def get_images_for_product(product_id: ProductID) -> Sequence[DbProductImage]:
    """Return images for the product."""
    return db.session.scalars(
        select(DbProductImage).filter_by(product_id=product_id)
    ).all()


def get_images_for_products(
    product_ids: set[ProductID],
) -> Sequence[DbProductImage]:
    """Return the images (if any) for each of the products."""
    return db.session.scalars(
        select(DbProductImage).filter(
            DbProductImage.product_id.in_(product_ids)
        )
    ).all()


def find_attached_product(
    attached_product_id: AttachedProductID,
) -> DbAttachedProduct | None:
    """Return the attached product with that ID, or `None` if not found."""
    return db.session.get(DbAttachedProduct, attached_product_id)


def get_attached_products_for_products(
    product_ids: set[ProductID],
) -> dict[ProductID, list[DbAttachedProduct]]:
    """Return the attached product with that ID, or `None` if not found."""
    if not product_ids:
        return {}

    rows = db.session.execute(
        select(DbAttachedProduct.attached_to_product_id, DbAttachedProduct)
        .filter(DbAttachedProduct.attached_to_product_id.in_(product_ids))
        .options(db.joinedload(DbAttachedProduct.product))
    ).all()

    attached_products_by_attached_to_product_id = defaultdict(list)
    for attached_to_product_id, db_attached_product in rows:
        attached_products_by_attached_to_product_id[
            attached_to_product_id
        ].append(db_attached_product)

    return attached_products_by_attached_to_product_id


def get_product_by_number(product_number: ProductNumber) -> DbProduct:
    """Return the product with that item number."""
    return db.session.execute(
        select(DbProduct).filter_by(item_number=product_number)
    ).scalar_one()


def get_products(
    product_ids: set[ProductID],
    *,
    only_currently_available: bool = False,
    only_directly_orderable: bool = False,
    only_not_requiring_separate_order: bool = False,
) -> Sequence[DbProduct]:
    """Return the products with those IDs."""
    if not product_ids:
        return []

    stmt = select(DbProduct).filter(DbProduct.id.in_(product_ids))

    if only_currently_available:
        now = datetime.utcnow()

        stmt = (
            stmt
            # Select only products that are available in between the
            # temporal boundaries for this product, if specified.
            .filter(
                db.or_(
                    DbProduct.available_from.is_(None),
                    now >= DbProduct.available_from,
                )
            ).filter(
                db.or_(
                    DbProduct.available_until.is_(None),
                    now < DbProduct.available_until,
                )
            )
        )

    if only_directly_orderable:
        stmt = stmt.filter_by(not_directly_orderable=False)

    if only_not_requiring_separate_order:
        stmt = stmt.filter_by(separate_order_required=False)

    return db.session.scalars(stmt).all()


def get_products_for_shop(shop_id: ShopID) -> Sequence[DbProduct]:
    """Return all products for that shop, ordered by product number."""
    return db.session.scalars(
        select(DbProduct)
        .filter_by(shop_id=shop_id)
        .order_by(DbProduct.item_number)
    ).all()


def get_products_for_shop_paginated(
    shop_id: ShopID,
    page: int,
    per_page: int,
    include_archived: bool,
    search_term: str | None,
) -> Pagination:
    """Return all products for that shop, paginated.

    Ordered by product number, reversed.
    """
    stmt = (
        select(DbProduct)
        .filter_by(shop_id=shop_id)
        .order_by(DbProduct.item_number.desc())
    )

    if not include_archived:
        stmt = stmt.filter_by(archived=False)

    if search_term:
        stmt = _filter_by_search_term(stmt, search_term)

    return paginate(stmt, page, per_page)


def _filter_by_search_term(stmt: Select, search_term: str) -> Select:
    terms = search_term.split(' ')
    clauses = map(_generate_search_clauses_for_term, terms)

    return stmt.filter(db.and_(*clauses))


def _generate_search_clauses_for_term(search_term: str) -> Select:
    ilike_pattern = f'%{search_term}%'

    return db.or_(
        DbProduct.item_number.ilike(ilike_pattern),
        DbProduct.name.ilike(ilike_pattern),
    )


def get_orderable_products(shop_id: ShopID) -> Sequence[DbProduct]:
    """Return the products which can be ordered from that shop, less the
    ones that are only orderable in a dedicated order.
    """
    now = datetime.utcnow()

    return db.session.scalars(
        select(DbProduct)
        .filter_by(shop_id=shop_id)
        .filter_by(not_directly_orderable=False)
        .filter_by(separate_order_required=False)
        # Select only products that are available in between the
        # temporal boundaries for this product, if specified.
        .filter(
            db.or_(
                DbProduct.available_from.is_(None),
                now >= DbProduct.available_from,
            )
        )
        .filter(
            db.or_(
                DbProduct.available_until.is_(None),
                now < DbProduct.available_until,
            )
        )
        .order_by(DbProduct.name)
    ).all()


def get_attachable_products(product_id: ProductID) -> Sequence[DbProduct]:
    """Return the products that can be attached to that product."""
    db_product = _get_db_product(product_id)

    db_attached_products = {
        db_attached.product for db_attached in db_product.attached_products
    }

    db_unattachable_products = {db_product}.union(db_attached_products)

    unattachable_product_ids = {
        db_product.id for db_product in db_unattachable_products
    }

    return db.session.scalars(
        select(DbProduct)
        .filter_by(shop_id=db_product.shop_id)
        .filter(db.not_(DbProduct.id.in_(unattachable_product_ids)))
        .order_by(DbProduct.item_number)
    ).all()


def sum_ordered_products_by_payment_state(
    shop_ids: set[ShopID],
) -> list[tuple[ShopID, ProductNumber, str, PaymentState, int]]:
    """Sum ordered products for those shops, grouped by order payment state."""
    subquery = (
        select(
            DbLineItem.product_id,
            DbOrder._payment_state.label('payment_state'),
            db.func.sum(DbLineItem.quantity).label('quantity'),
        )
        .join(DbOrder)
        .group_by(DbLineItem.product_id, DbOrder._payment_state)
        .subquery()
    )

    rows = db.session.execute(
        select(
            DbProduct.shop_id,
            DbProduct.item_number,
            DbProduct.name,
            subquery.c.payment_state,
            subquery.c.quantity,
        )
        .outerjoin(
            subquery,
            db.and_(DbProduct.id == subquery.c.product_id),
        )
        .filter(DbProduct.shop_id.in_(shop_ids))
        .order_by(DbProduct.item_number, subquery.c.payment_state)
    ).all()

    shop_ids_and_product_numbers_and_names = {
        (row[0], row[1], row[2]) for row in rows
    }  # Remove duplicates.

    quantities = {}

    for (
        shop_id,
        product_number,
        name,
        payment_state_name,
        quantity,
    ) in rows:
        if payment_state_name is None:
            continue

        payment_state = PaymentState[payment_state_name]
        key = (shop_id, product_number, name, payment_state)

        quantities[key] = quantity

    def generate():
        for shop_id, product_number, name in sorted(
            shop_ids_and_product_numbers_and_names
        ):
            for payment_state in PaymentState:
                key = (shop_id, product_number, name, payment_state)
                quantity = quantities.get(key, 0)

                yield (
                    shop_id,
                    product_number,
                    name,
                    payment_state,
                    quantity,
                )

    return list(generate())
