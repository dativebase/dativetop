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
        new_url = 'http://localhost:1111'
        request = testing.DummyRequest(
            json_body={'url': new_url}, method='PUT')
        response = v.old_service(request)
        self.assertEqual(2, len(self.session.query(m.OLDService).all()))
        self.assertEqual(new_url, response['url'])
        new_new_url = 'http://localhost:2222'
        request = testing.DummyRequest(
            json_body={'url': new_new_url}, method='POST')
        response = v.old_service(request)
        self.assertEqual(
            'The old_service only recognizes GET and PUT requests.',
            response['error'])
        v.old_service(testing.DummyRequest(json_body={'url': new_new_url},
                                           method='PUT'))
        old_service_rows = self.session.query(m.OLDService).all()
        self.assertEqual(3, len(old_service_rows))
        self.assertEqual(1, len(set([os.history_id for os in old_service_rows])))

    def test_old_service_url_validation(self):
        import dativetopserver.views as v
        self.assertEqual('scheme is not http',
                         v.validate_old_service_url('https://localhost:1111'))
        self.assertEqual('no port',
                         v.validate_old_service_url('http://localhost'))
        self.assertIn('hostname invalid',
                      v.validate_old_service_url('http://myhost:1111'))
        self.assertEqual('path is not empty',
                      v.validate_old_service_url('http://127.0.0.1:1111/foo'))
        self.assertIsNone(v.validate_old_service_url('http://127.0.0.1:1111/'))
        self.assertIsNone(v.validate_old_service_url('http://localhost:5678'))
