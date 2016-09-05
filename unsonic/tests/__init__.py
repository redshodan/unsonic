import unittest

from pyramid import testing

from ..models import Session


class TestCase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from ..models import Base
        # DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        # DBSession.remove()
        testing.tearDown()
