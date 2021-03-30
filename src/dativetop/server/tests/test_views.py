import transaction
import unittest

from pyramid import testing


def _initTestingDB():
    from sqlalchemy import create_engine
    from dativetopserver.models import (Base, DBSession)
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession


class ViewsTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_old_service_api(self):
        import dativetopserver.views as v
        import dativetopserver.models as m
        self.assertEqual([], self.session.query(m.OLDService).all())
        request = testing.DummyRequest(method='GET')
        response = v.old_service(request)
        self.assertEqual(1, len(self.session.query(m.OLDService).all()))
        self.assertEqual(m.DEFAULT_OLD_SERVICE_URL, response['url'])
        request = testing.DummyRequest(
            json_body={'url': 'dog'}, method='PUT')
        response = v.old_service(request)
        self.assertEqual(2, len(self.session.query(m.OLDService).all()))
        self.assertEqual('dog', response['url'])
        request = testing.DummyRequest(
            json_body={'url': 'dog'}, method='POST')
        response = v.old_service(request)
        self.assertEqual(
            'The old_service only recognizes GET and PUT requests.',
            response['error'])
        v.old_service(testing.DummyRequest(json_body={'url': 'cat'},
                                           method='PUT'))
        old_service_rows = self.session.query(m.OLDService).all()
        self.assertEqual(3, len(old_service_rows))
        self.assertEqual(1, len(set([os.history_id for os in old_service_rows])))
