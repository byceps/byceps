"""
byceps.services.shop.article.dbmodels.attached_article
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....database import db, generate_uuid

from ..models import ArticleID

from .article import DbArticle


class DbAttachedArticle(db.Model):
    """An article that is attached to another article."""

    __tablename__ = 'shop_attached_articles'
    __table_args__ = (
        db.UniqueConstraint('article_id', 'attached_to_article_id'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    article_id = db.Column(
        db.Uuid, db.ForeignKey('shop_articles.id'), nullable=False, index=True
    )
    article = db.relationship(
        DbArticle,
        foreign_keys=[article_id],
        backref=db.backref('articles_attached_to', collection_class=set),
    )
    quantity = db.Column(
        db.Integer, db.CheckConstraint('quantity > 0'), nullable=False
    )
    attached_to_article_id = db.Column(
        db.Uuid, db.ForeignKey('shop_articles.id'), nullable=False, index=True
    )
    attached_to_article = db.relationship(
        DbArticle,
        foreign_keys=[attached_to_article_id],
        backref=db.backref('attached_articles', collection_class=set),
    )

    def __init__(
        self,
        article_id: ArticleID,
        quantity: int,
        attached_to_article_id: ArticleID,
    ) -> None:
        self.article_id = article_id
        self.quantity = quantity
        self.attached_to_article_id = attached_to_article_id
