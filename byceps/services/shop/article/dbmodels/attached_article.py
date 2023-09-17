"""
byceps.services.shop.article.dbmodels.attached_article
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db, generate_uuid7
from byceps.services.shop.article.models import ArticleID, AttachedArticleID

from .article import DbArticle


class DbAttachedArticle(db.Model):
    """An article that is attached to another article."""

    __tablename__ = 'shop_attached_articles'
    __table_args__ = (
        db.UniqueConstraint('article_id', 'attached_to_article_id'),
    )

    id: Mapped[AttachedArticleID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    article_id: Mapped[ArticleID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_articles.id'), index=True
    )
    article: Mapped[DbArticle] = relationship(
        DbArticle,
        foreign_keys=[article_id],
        backref=db.backref('articles_attached_to', collection_class=set),
    )
    quantity: Mapped[int] = mapped_column(db.CheckConstraint('quantity > 0'))
    attached_to_article_id: Mapped[ArticleID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_articles.id'), index=True
    )
    attached_to_article: Mapped[DbArticle] = relationship(
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
