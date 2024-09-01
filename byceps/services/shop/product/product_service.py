"""
byceps.services.shop.product.product_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from moneyed import Money
from sqlalchemy import delete, select, update
from sqlalchemy.sql import Select

from byceps.database import db, paginate, Pagination
from byceps.services.shop.order.dbmodels.line_item import DbLineItem
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.order import PaymentState
from byceps.services.shop.shop.models import ShopID
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from . import product_domain_service
from .dbmodels.product import DbProduct, DbProductImage
from .dbmodels.attached_product import DbAttachedProduct
from .errors import NoProductsAvailableError
from .models import (
    Product,
    ProductAttachment,
    ProductCollection,
    ProductCollectionItem,
    ProductCompilation,
    ProductCompilationBuilder,
    ProductID,
    ProductImage,
    ProductNumber,
    ProductType,
    ProductTypeParams,
    AttachedProductID,
)


class UnknownProductIdError(ValueError):
    pass


def create_product(
    shop_id: ShopID,
    item_number: ProductNumber,
    type_: ProductType,
    name: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    processing_required: bool,
    *,
    type_params: ProductTypeParams | None = None,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Product:
    """Create a product."""
    product = product_domain_service.create_product(
        shop_id,
        item_number,
        type_,
        name,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
        type_params=type_params,
        available_from=available_from,
        available_until=available_until,
        not_directly_orderable=not_directly_orderable,
        separate_order_required=separate_order_required,
    )

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

    return _db_entity_to_product(db_product)


def create_ticket_product(
    shop_id: ShopID,
    item_number: ProductNumber,
    name: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    ticket_category_id: TicketCategoryID,
    *,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Product:
    """Create a product that represents a ticket."""
    type_params: ProductTypeParams = {
        'ticket_category_id': str(ticket_category_id),
    }
    processing_required = True

    return create_product(
        shop_id,
        item_number,
        ProductType.ticket,
        name,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
        type_params=type_params,
        available_from=available_from,
        available_until=available_until,
        not_directly_orderable=not_directly_orderable,
        separate_order_required=separate_order_required,
    )


def create_ticket_bundle_product(
    shop_id: ShopID,
    item_number: ProductNumber,
    name: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
    *,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Product:
    """Create a product that represents a ticket bundle."""
    type_params: ProductTypeParams = {
        'ticket_category_id': str(ticket_category_id),
        'ticket_quantity': ticket_quantity,
    }
    processing_required = True

    return create_product(
        shop_id,
        item_number,
        ProductType.ticket_bundle,
        name,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
        type_params=type_params,
        available_from=available_from,
        available_until=available_until,
        not_directly_orderable=not_directly_orderable,
        separate_order_required=separate_order_required,
    )


def update_product(
    product_id: ProductID,
    name: str,
    price: Money,
    tax_rate: Decimal,
    available_from: datetime | None,
    available_until: datetime | None,
    total_quantity: int,
    max_quantity_per_order: int,
    not_directly_orderable: bool,
    separate_order_required: bool,
    archived: bool,
) -> Product:
    """Update the product."""
    db_product = _get_db_product(product_id)

    db_product.name = name
    db_product.price_amount = price.amount
    db_product.price_currency = price.currency
    db_product.tax_rate = tax_rate
    db_product.available_from = available_from
    db_product.available_until = available_until
    db_product.total_quantity = total_quantity
    db_product.max_quantity_per_order = max_quantity_per_order
    db_product.not_directly_orderable = not_directly_orderable
    db_product.separate_order_required = separate_order_required
    db_product.archived = archived

    db.session.commit()

    return _db_entity_to_product(db_product)


def create_product_image(
    product: Product, url: str, url_preview: str, position: int
) -> ProductImage:
    """Create an image for a product."""
    # Verify if product exists.
    _get_db_product(product.id)

    image = product_domain_service.create_product_image(
        product, url, url_preview, position
    )

    db_image = DbProductImage(
        image.id,
        image.product_id,
        image.url,
        image.url_preview,
        image.position,
    )
    db.session.add(db_image)
    db.session.commit()

    return image


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
    product_id: ProductID, quantity_to_increase_by: int, *, commit: bool = True
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
    product_id: ProductID, quantity_to_decrease_by: int, *, commit: bool = True
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


def find_product(product_id: ProductID) -> Product | None:
    """Return the product with that ID, or `None` if not found."""
    db_product = find_db_product(product_id)

    if db_product is None:
        return None

    return _db_entity_to_product(db_product)


def get_product(product_id: ProductID) -> Product:
    """Return the product with that ID.

    Raise an exception if not found.
    """
    product = find_product(product_id)

    if product is None:
        raise UnknownProductIdError(product_id)

    return product


def find_db_product(product_id: ProductID) -> DbProduct | None:
    """Return the database entity for the product with that ID, or
    `None` if not found.
    """
    return db.session.get(DbProduct, product_id)


def _get_db_product(product_id: ProductID) -> DbProduct:
    """Return the database entity for the product with that id.

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


def get_images_for_product(product_id: ProductID) -> list[ProductImage]:
    """Return images for the product."""
    db_images = db.session.scalars(
        select(DbProductImage).filter_by(product_id=product_id)
    ).all()

    return [_db_entity_to_product_image(db_image) for db_image in db_images]


def get_images_for_products(
    product_ids: set[ProductID],
) -> dict[ProductID, list[ProductImage]]:
    """Return the images (if any) for each of the products."""
    db_images = db.session.scalars(
        select(DbProductImage).filter(
            DbProductImage.product_id.in_(product_ids)
        )
    ).all()

    images = [_db_entity_to_product_image(db_image) for db_image in db_images]

    images.sort(key=lambda image: (image.product_id, image.position))

    images_by_product_id = defaultdict(list)
    for image in images:
        images_by_product_id[image.product_id].append(image)

    return dict(images_by_product_id)


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


def get_product_by_number(product_number: ProductNumber) -> Product:
    """Return the product with that item number."""
    db_product = db.session.execute(
        select(DbProduct).filter_by(item_number=product_number)
    ).scalar_one()

    return _db_entity_to_product(db_product)


def get_products(product_ids: set[ProductID]) -> list[Product]:
    """Return the products with those IDs."""
    if not product_ids:
        return []

    db_products = db.session.scalars(
        select(DbProduct).filter(DbProduct.id.in_(product_ids))
    ).all()

    return [_db_entity_to_product(db_product) for db_product in db_products]


def get_products_for_shop(shop_id: ShopID) -> list[Product]:
    """Return all products for that shop, ordered by product number."""
    db_products = db.session.scalars(
        select(DbProduct)
        .filter_by(shop_id=shop_id)
        .order_by(DbProduct.item_number)
    ).all()

    return [_db_entity_to_product(db_product) for db_product in db_products]


def get_products_for_shop_paginated(
    shop_id: ShopID,
    page: int,
    per_page: int,
    *,
    search_term=None,
) -> Pagination:
    """Return all products for that shop, paginated.

    Ordered by product number, reversed.
    """
    stmt = (
        select(DbProduct)
        .filter_by(shop_id=shop_id)
        .order_by(DbProduct.item_number.desc())
    )

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


def get_product_compilation_for_orderable_products(
    shop_id: ShopID,
) -> Result[ProductCompilation, NoProductsAvailableError]:
    """Return a compilation of the products which can be ordered from
    that shop, less the ones that are only orderable in a dedicated
    order.
    """
    now = datetime.utcnow()

    db_orderable_products = db.session.scalars(
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

    if not db_orderable_products:
        return Err(NoProductsAvailableError())

    compilation_builder = ProductCompilationBuilder()

    for db_product in db_orderable_products:
        product = _db_entity_to_product(db_product)
        compilation_builder.append_product(product)

        product_attachments = _get_product_attachments(
            db_product.attached_products
        )
        for product_attachment in product_attachments:
            compilation_builder.append_product(
                product_attachment.attached_product,
                fixed_quantity=product_attachment.attached_quantity,
            )

    compilation = compilation_builder.build()

    return Ok(compilation)


def get_product_compilation_for_single_product(
    product_id: ProductID,
) -> ProductCompilation:
    """Return a compilation built from just the given product (with a
    quantity of one) plus the products attached to it (if any).
    """
    db_product = _get_db_product(product_id)

    compilation_builder = ProductCompilationBuilder()

    product = _db_entity_to_product(db_product)
    compilation_builder.append_product(product, fixed_quantity=1)

    product_attachments = _get_product_attachments(db_product.attached_products)
    for product_attachment in product_attachments:
        compilation_builder.append_product(
            product_attachment.attached_product,
            fixed_quantity=product_attachment.attached_quantity,
        )

    return compilation_builder.build()


def get_product_compilations_for_single_products(
    product_ids: set[ProductID],
) -> dict[ProductID, ProductCompilation]:
    """Return a compilation of the products (with a quantity of one)
    plus the products attached to it (if any).
    """
    if not product_ids:
        return {}

    compilations_by_product_id: dict[ProductID, ProductCompilation] = {}

    db_products = db.session.scalars(
        select(DbProduct).filter(DbProduct.id.in_(product_ids))
    ).all()

    attached_products_by_attached_to_product_id = (
        get_attached_products_for_products(product_ids)
    )

    for db_product in db_products:
        compilation_builder = ProductCompilationBuilder()

        product = _db_entity_to_product(db_product)
        compilation_builder.append_product(product, fixed_quantity=1)

        db_attached_products = attached_products_by_attached_to_product_id[
            db_product.id
        ]
        product_attachments = _get_product_attachments(db_attached_products)
        for product_attachment in product_attachments:
            compilation_builder.append_product(
                product_attachment.attached_product,
                fixed_quantity=product_attachment.attached_quantity,
            )

        compilation = compilation_builder.build()

        compilations_by_product_id[product.id] = compilation

    return compilations_by_product_id


def get_attachable_products(product_id: ProductID) -> list[Product]:
    """Return the products that can be attached to that product."""
    db_product = _get_db_product(product_id)

    db_attached_products = {
        db_attached.product for db_attached in db_product.attached_products
    }

    db_unattachable_products = {db_product}.union(db_attached_products)

    unattachable_product_ids = {
        db_product.id for db_product in db_unattachable_products
    }

    db_products = db.session.scalars(
        select(DbProduct)
        .filter_by(shop_id=db_product.shop_id)
        .filter(db.not_(DbProduct.id.in_(unattachable_product_ids)))
        .order_by(DbProduct.item_number)
    ).all()

    return [_db_entity_to_product(db_product) for db_product in db_products]


def get_product_collection_for_product_compilation(
    title: str, compilation: ProductCompilation
) -> ProductCollection:
    """Create product collection from product compilation."""
    return ProductCollection(
        title=title,
        items=[
            ProductCollectionItem(
                product=compilation_item.product,
                fixed_quantity=compilation_item.fixed_quantity,
                has_fixed_quantity=compilation_item.has_fixed_quantity,
            )
            for compilation_item in compilation
        ],
    )


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


def _db_entity_to_product(db_product: DbProduct) -> Product:
    return Product(
        id=db_product.id,
        shop_id=db_product.shop_id,
        item_number=db_product.item_number,
        type_=db_product.type_,
        type_params=db_product.type_params or {},
        name=db_product.name,
        price=db_product.price,
        tax_rate=db_product.tax_rate,
        available_from=db_product.available_from,
        available_until=db_product.available_until,
        total_quantity=db_product.total_quantity,
        quantity=db_product.quantity,
        max_quantity_per_order=db_product.max_quantity_per_order,
        not_directly_orderable=db_product.not_directly_orderable,
        separate_order_required=db_product.separate_order_required,
        processing_required=db_product.processing_required,
        archived=db_product.archived,
    )


def _db_entity_to_product_image(db_image: DbProductImage) -> ProductImage:
    return ProductImage(
        id=db_image.id,
        product_id=db_image.product_id,
        url=db_image.url,
        url_preview=db_image.url_preview,
        position=db_image.position,
    )


def _get_product_attachments(
    db_attached_products: list[DbProduct],
) -> list[ProductAttachment]:
    return [
        ProductAttachment(
            attached_product=_db_entity_to_product(db_attached_product.product),
            attached_quantity=db_attached_product.quantity,
        )
        for db_attached_product in db_attached_products
    ]
