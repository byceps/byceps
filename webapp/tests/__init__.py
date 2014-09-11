# -*- coding: utf-8 -*-

from unittest import TestCase

from byceps.application import create_app
from byceps.blueprints.brand.models import Brand
from byceps.blueprints.party.models import Party
from byceps.database import db


class AbstractAppTestCase(TestCase):

    def setUp(self):
        self.app = create_app('test', initialize=False)

        self.db = db
        db.app = self.app
        db.create_all()

        self.create_brand_and_party()

        self.client = self.app.test_client()

    def create_brand_and_party(self):
        brand = Brand(id='acme', title='ACME')
        db.session.add(brand)
        party = Party(id='acme-2014', brand=brand, title='ACME 2014')
        db.session.add(party)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
