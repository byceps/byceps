# -*- coding: utf-8 -*-

from unittest import TestCase

from byceps.application import create_app
from byceps.database import db


class AbstractAppTestCase(TestCase):

    def setUp(self):
        self.app = create_app('test')

        db.app = self.app
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
