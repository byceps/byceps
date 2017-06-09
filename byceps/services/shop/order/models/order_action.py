"""
byceps.services.shop.order.models.order_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict

from .....database import db, generate_uuid

from ...article.models.article import Article, ArticleNumber


class OrderAction(db.Model):
    """A procedure to execute when an order for that article is marked
    as paid.
    """
    __tablename__ = 'shop_order_actions'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    article_number = db.Column(db.Unicode(20), db.ForeignKey('shop_articles.item_number'), index=True, nullable=False)
    article = db.relationship(Article, backref='order_actions')
    procedure = db.Column(db.Unicode(40), nullable=False)
    parameters = db.Column(db.JSONB, nullable=False)

    def __init__(self, article_number: ArticleNumber, procedure: str,
                 parameters: Dict[str, Any]) -> None:
        self.article_number = article_number
        self.procedure = procedure
        self.parameters = parameters
