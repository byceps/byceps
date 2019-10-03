"""
byceps.services.shop.article.models.attached_article
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .....database import db, generate_uuid

from .article import Article


class AttachedArticle(db.Model):
    """An article that is attached to another article."""
    __tablename__ = 'shop_attached_articles'
    __table_args__ = (
        db.UniqueConstraint('article_number', 'attached_to_article_number'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    article_number = db.Column(db.UnicodeText,
                               db.ForeignKey('shop_articles.item_number'),
                               nullable=False, index=True)
    article = db.relationship(Article, foreign_keys=[article_number],
                              backref=db.backref('articles_attached_to', collection_class=set))
    quantity = db.Column(db.Integer, db.CheckConstraint('quantity > 0'), nullable=False)
    attached_to_article_number = db.Column(db.UnicodeText,
                                           db.ForeignKey('shop_articles.item_number'),
                                           nullable=False, index=True)
    attached_to_article = db.relationship(Article, foreign_keys=[attached_to_article_number],
                                          backref=db.backref('attached_articles', collection_class=set))

    def __init__(
        self, article: Article, quantity: int, attached_to_article: Article
    ) -> None:
        self.article = article
        self.quantity = quantity
        self.attached_to_article = attached_to_article
