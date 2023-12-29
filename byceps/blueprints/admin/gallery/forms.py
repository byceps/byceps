"""
byceps.blueprints.admin.gallery.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired, ValidationError

from byceps.services.brand.models import BrandID
from byceps.services.gallery import gallery_service
from byceps.util.l10n import LocalizedForm


class GalleryCreateForm(LocalizedForm):
    slug = StringField(lazy_gettext('Slug'), [InputRequired()])
    title = StringField(lazy_gettext('Title'), [InputRequired()])
    hidden = BooleanField(lazy_gettext('hidden'), [])

    def __init__(self, brand_id: BrandID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._brand_id = brand_id

    @staticmethod
    def validate_slug(form, field):
        slug = field.data.strip()

        if not gallery_service.is_slug_available(form._brand_id, slug):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )
