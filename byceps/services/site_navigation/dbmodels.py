"""
byceps.services.site_navigation.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.ext.orderinglist import ordering_list

from byceps.database import db
from byceps.services.language.dbmodels import DbLanguage
from byceps.services.site.models import SiteID
from byceps.util.uuid import generate_uuid7

from .models import NavItemID, NavItemTargetType, NavMenuID


class DbNavMenu(db.Model):
    """A navigation menu."""

    __tablename__ = 'site_nav_menus'
    __table_args__ = (db.UniqueConstraint('site_id', 'name', 'language_code'),)

    id: Mapped[NavMenuID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    site_id: Mapped[SiteID] = mapped_column(
        db.UnicodeText, db.ForeignKey('sites.id'), index=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    language_code: Mapped[str] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('languages.code'),
        index=True,
    )
    language: Mapped[DbLanguage] = relationship(DbLanguage)
    hidden: Mapped[bool]
    parent_menu_id: Mapped[NavMenuID | None] = mapped_column(
        db.Uuid, db.ForeignKey('site_nav_menus.id')
    )

    def __init__(
        self,
        site_id: SiteID,
        name: str,
        language_code: str,
        hidden: bool,
        *,
        parent_menu_id: NavMenuID | None = None,
    ) -> None:
        self.site_id = site_id
        self.name = name
        self.language_code = language_code
        self.hidden = hidden
        self.parent_menu_id = parent_menu_id


class DbNavItem(db.Model):
    """An item of a navigation menu."""

    __tablename__ = 'site_nav_menu_items'
    __table_args__ = (
        db.UniqueConstraint('menu_id', 'parent_item_id', 'position'),
    )

    id: Mapped[NavItemID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    menu_id: Mapped[NavMenuID] = mapped_column(
        db.Uuid, db.ForeignKey('site_nav_menus.id'), index=True
    )
    menu: Mapped[DbNavMenu] = relationship(
        DbNavMenu,
        backref=db.backref(
            'items',
            order_by='byceps.services.site_navigation.dbmodels.DbNavItem.position',
            collection_class=ordering_list('position', count_from=1),
        ),
    )
    parent_item_id: Mapped[NavItemID | None] = mapped_column(
        db.Uuid,
        db.ForeignKey('site_nav_menu_items.id'),
        index=True,
    )
    position: Mapped[int]
    _target_type: Mapped[str] = mapped_column('target_type', db.UnicodeText)
    target: Mapped[str] = mapped_column(db.UnicodeText)
    label: Mapped[str] = mapped_column(db.UnicodeText)
    current_page_id: Mapped[str] = mapped_column(db.UnicodeText)
    hidden: Mapped[bool]

    def __init__(
        self,
        menu_id: NavMenuID,
        parent_item_id: NavItemID | None,
        target_type: NavItemTargetType,
        target: str,
        label: str,
        current_page_id: str,
        hidden: bool,
    ) -> None:
        self.menu_id = menu_id
        self.parent_item_id = parent_item_id
        self.target_type = target_type
        self.target = target
        self.label = label
        self.current_page_id = current_page_id
        self.hidden = hidden

    @hybrid_property
    def target_type(self) -> NavItemTargetType:
        return NavItemTargetType[self._target_type]

    @target_type.setter
    def target_type(self, target_type: NavItemTargetType) -> None:
        self._target_type = target_type.name
