import transaction
import unittest
from uuid import uuid4

from pyramid import testing
from sqlalchemy import desc


def is_uuid_str(x):
    return (isinstance(x, str) and
            [8, 4, 4, 4, 12] == [len([c for c in y if c in '0123456789abcdef'])
                                 for y in x.split('-')])


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
            'The /old_service endpoint only recognizes GET and PUT requests.',
            response['error'])
        v.old_service(testing.DummyRequest(json_body={'url': new_new_url},
                                           method='PUT'))
        old_service_rows = self.session.query(m.OLDService).all()
        self.assertEqual(3, len(old_service_rows))
        self.assertEqual(1, len(set([os.history_id for os in old_service_rows])))
        request = testing.DummyRequest(
            json_body={'url': m.get_dative_app().url}, method='PUT')
        response = v.old_service(request)
        self.assertEqual('OLD Service URL must be different from Dative App URL',
                         response['error'])

    def test_dative_app_api(self):
        import dativetopserver.views as v
        import dativetopserver.models as m
        self.assertEqual([], self.session.query(m.DativeApp).all())
        request = testing.DummyRequest(method='GET')
        response = v.dative_app(request)
        self.assertEqual(1, len(self.session.query(m.DativeApp).all()))
        self.assertEqual(m.DEFAULT_DATIVE_APP_URL, response['url'])
        new_url = 'http://localhost:1111'
        request = testing.DummyRequest(
            json_body={'url': new_url}, method='PUT')
        response = v.dative_app(request)
        self.assertEqual(2, len(self.session.query(m.DativeApp).all()))
        self.assertEqual(new_url, response['url'])
        new_new_url = 'http://localhost:2222'
        request = testing.DummyRequest(
            json_body={'url': new_new_url}, method='POST')
        response = v.dative_app(request)
        self.assertEqual(
            'The /dative_app endpoint only recognizes GET and PUT requests.',
            response['error'])
        v.dative_app(testing.DummyRequest(json_body={'url': new_new_url},
                                           method='PUT'))
        dative_app_rows = self.session.query(m.DativeApp).all()
        self.assertEqual(3, len(dative_app_rows))
        self.assertEqual(1, len(set([os.history_id for os in dative_app_rows])))
        request = testing.DummyRequest(
            json_body={'url': m.get_old_service().url}, method='PUT')
        response = v.dative_app(request)
        self.assertEqual('Dative App URL must be different from OLD Service URL',
                         response['error'])


    def test_local_url_validation(self):
        import dativetopserver.views as v
        self.assertEqual('scheme is not http',
                         v.validate_local_url('https://localhost:1111'))
        self.assertEqual('no port',
                         v.validate_local_url('http://localhost'))
        self.assertIn('hostname invalid',
                      v.validate_local_url('http://myhost:1111'))
        self.assertEqual('path is not empty',
                      v.validate_local_url('http://127.0.0.1:1111/foo'))
        self.assertIsNone(v.validate_local_url('http://127.0.0.1:1111/'))
        self.assertIsNone(v.validate_local_url('http://localhost:5678'))


    def test_old_api(self):
        import dativetopserver.views as v
        import dativetopserver.models as m
        self.assertEqual([], self.session.query(m.OLD).all())
        request = testing.DummyRequest(
            method='POST',
            json_body={'slug': 'oka'})
        response = v.olds(request)
        self.assertEqual(1, len(self.session.query(m.OLD).all()))
        self.assertEqual('oka', response['slug'])
        self.assertEqual('oka', response['name'])
        self.assertEqual([None, None, None, False],
                         [response['leader'], response['username'],
                          response['password'], response['is_auto_syncing']])

        # Valid OLD Creation
        valid_input = {
            'slug': 'bla',
            'name': 'Blackfoot',
            'leader': 'https://do.old.org/bla',
            'username': 'someuser',
            'password': 'somepassword',
            'is_auto_syncing': True
        }
        request = testing.DummyRequest(
            method='POST', json_body=valid_input)
        response = v.olds(request)
        self.assertEqual(2, len(self.session.query(m.OLD).all()))
        for attr, val in valid_input.items():
            self.assertEqual(val, response[attr])
        self.assertTrue(is_uuid_str(response['id']), 'OLD.id is a UUID')

        # Invalid OLD Creation 1: is_auto_syncing not boolean
        invalid_input = valid_input.copy()
        invalid_input['slug'] = 'invalidbla'
        invalid_input['is_auto_syncing'] = 1
        response = v.olds(
            testing.DummyRequest(method='POST', json_body=invalid_input))
        self.assertEqual(2, len(self.session.query(m.OLD).all()))
        self.assertEqual('value must be a boolean', response['error'])

        # Invalid OLD Creation 2: leader not string
        invalid_input = valid_input.copy()
        invalid_input['slug'] = 'invalidbla'
        invalid_input['leader'] = 1
        response = v.olds(
            testing.DummyRequest(method='POST', json_body=invalid_input))
        self.assertEqual(2, len(self.session.query(m.OLD).all()))
        self.assertEqual('value must be a string', response['error'])

        # Fetch the created OLDs via the API
        response = v.olds(testing.DummyRequest(method='GET'))
        self.assertEqual(2, len(response))
        self.assertEqual(set(['oka', 'bla']),
                         set([o['slug'] for o in response]))

        # Fetch the first created OLD via the API
        old = response[0]
        old_id = old['id']
        response = v.old(testing.DummyRequest(method='GET',
                                              matchdict={'old_id': old_id}))
        self.assertEqual(old, response)

        # Fail to fetch an OLD using an invalid ID
        response = v.old(testing.DummyRequest(method='GET',
                                              matchdict={'old_id': str(uuid4())}))
        self.assertEqual('No OLD with supplied ID', response['error'])

        # Update the first OLD
        valid_input = {
            'name': 'Okanagan',
            'leader': 'https://do.old.org/oka',
            'username': 'someuser',
            'password': 'somepassword',
            'is_auto_syncing': True
        }
        request = testing.DummyRequest(
            method='PUT', json_body=valid_input, matchdict={'old_id': old_id})
        response = v.old(request)
        self.assertEqual(3, len(self.session.query(m.OLD).all())) # history retained
        self.assertEqual(2, len(v.olds(testing.DummyRequest(method='GET'))))
        for attr, val in valid_input.items():
            self.assertEqual(val, response[attr])
        self.assertEqual(old_id, response['id'])

        # Updates to slug and state silently fail
        vacuous_input = {'slug': 'okana', 'state': m.old_state.failed_to_sync}
        request = testing.DummyRequest(
            method='PUT', json_body=vacuous_input, matchdict={'old_id': old_id})
        vacuous_response = v.old(request)
        self.assertEqual(3, len(self.session.query(m.OLD).all())) # no db changes
        self.assertEqual(response, vacuous_response)

        # Silent update fails accompanied by successful ones do mutate db
        valid_input = {'slug': 'okana',
                       'state': m.old_state.failed_to_sync,
                       'name': 'Nsyilxcen'}
        request = testing.DummyRequest(
            method='PUT', json_body=valid_input, matchdict={'old_id': old_id})
        response = v.old(request)
        self.assertEqual(4, len(self.session.query(m.OLD).all())) # db changes
        self.assertEqual('Nsyilxcen', response['name'])

        # Transition the OLD state
        request = testing.DummyRequest(
            method='PUT', json_body={'state': 'syncing'},
            matchdict={'old_id': old_id})
        response = v.old_state(request)
        self.assertEqual(5, len(self.session.query(m.OLD).all())) # db changes
        self.assertEqual('syncing', response['state'])

        # Vacuous transition has no effect
        request = testing.DummyRequest(
            method='PUT', json_body={'state': 'syncing'},
            matchdict={'old_id': old_id})
        response = v.old_state(request)
        self.assertEqual(5, len(self.session.query(m.OLD).all())) # db changes
        self.assertEqual('syncing', response['state'])

        # Transition with a numeric state fails
        request = testing.DummyRequest(
            method='PUT', json_body={'state': 0},
            matchdict={'old_id': old_id})
        response = v.old_state(request)
        self.assertIn('state must be one of', response['error'])

        # An illegal transition (syncing => not_synced) fails
        request = testing.DummyRequest(
            method='PUT', json_body={'state': 'not_synced'},
            matchdict={'old_id': old_id})
        response = v.old_state(request)
        self.assertEqual(5, len(self.session.query(m.OLD).all())) # no db changes
        self.assertEqual('illegal state transition', response['error'])

        # A legal transition (syncing => synced) succeeds
        request = testing.DummyRequest(
            method='PUT', json_body={'state': 'synced'},
            matchdict={'old_id': old_id})
        response = v.old_state(request)
        self.assertEqual(6, len(self.session.query(m.OLD).all())) # db changes
        self.assertEqual('synced', response['state'])

        # Delete the OLD
        request = testing.DummyRequest(
            method='DELETE', matchdict={'old_id': old_id})
        response = v.old(request)
        self.assertEqual(6, len(self.session.query(m.OLD).all())) # end updated
        self.assertGreater(m.get_now(),
                           self.session.query(m.OLD).filter(
                               m.OLD.history_id == old_id).order_by(
                                   desc(m.OLD.start)).first().end)

    def test_sync_old_command_api(self):
        import dativetopserver.views as v
        import dativetopserver.models as m

        # try to pop a command from an empty queue
        request = testing.DummyRequest(method='PUT')
        response = v.sync_old_commands(request)
        self.assertEqual('No commands in the queue', response['error'])

        # try to enqueue a command for a non-existent OLD
        request = testing.DummyRequest(method='POST', json_body={'old_id': 'abc'})
        response = v.sync_old_commands(request)
        self.assertEqual('No OLD with supplied ID', response['error'])
        request = testing.DummyRequest(method='POST', json_body={})
        response = v.sync_old_commands(request)
        self.assertEqual('OLD ID is required', response['error'])

        # Create some OLDs
        bla = v.olds(testing.DummyRequest(
            method='POST', json_body= {
                'slug': 'bla',
                'name': 'Blackfoot',
                'leader': 'https://do.old.org/bla',
                'username': 'someuser',
                'password': 'somepassword',
                'is_auto_syncing': True}))
        oka = v.olds(testing.DummyRequest(
            method='POST', json_body= {
                'slug': 'oka',
                'name': 'Okanagan',
                'leader': 'https://do.old.org/oka',
                'username': 'someuser',
                'password': 'somepassword',
                'is_auto_syncing': True}))
        fra = v.olds(testing.DummyRequest(
            method='POST', json_body= {
                'slug': 'fra',
                'name': 'French',
                'leader': 'https://do.old.org/fra',
                'username': 'someuser',
                'password': 'somepassword',
                'is_auto_syncing': True}))
        self.assertEqual(3, len(v.olds(testing.DummyRequest(method='GET'))))

        # Create 3 commands, confirm they're un-acked
        bla_cmd = v.sync_old_commands(testing.DummyRequest(
            method='POST', json_body={'old_id': bla['id']}))
        oka_cmd = v.sync_old_commands(testing.DummyRequest(
            method='POST', json_body={'old_id': oka['id']}))
        fra_cmd = v.sync_old_commands(testing.DummyRequest(
            method='POST', json_body={'old_id': fra['id']}))
        self.assertEqual(bla['id'], bla_cmd['old_id'])
        self.assertFalse(bla_cmd['acked'])
        self.assertEqual(oka['id'], oka_cmd['old_id'])
        self.assertFalse(oka_cmd['acked'])
        self.assertEqual(fra['id'], fra_cmd['old_id'])
        self.assertFalse(fra_cmd['acked'])

        # Attempting to create a command for an OLD that already has one will
        # return the existing command
        new_bla_cmd = v.sync_old_commands(testing.DummyRequest(
            method='POST', json_body={'old_id': bla['id']}))
        self.assertEqual(bla_cmd, new_bla_cmd)

        # We can fetch the command idempotently, if we want:
        fetched_bla_cmd = v.sync_old_command(testing.DummyRequest(
            method='GET', matchdict={'command_id': bla_cmd['id']}))
        self.assertEqual(bla_cmd, fetched_bla_cmd)

        # The first command to pop will be bla
        popped_bla = v.sync_old_commands(testing.DummyRequest(method='PUT'))
        self.assertTrue(popped_bla['acked'])
        self.assertEqual(popped_bla['old_id'], bla['id'])

        # We can fetch the bla command after popping it
        fetched_bla = v.sync_old_command(testing.DummyRequest(
            method='GET', matchdict={'command_id': popped_bla['id']}))
        self.assertEqual(fetched_bla, popped_bla)

        # Can complete the acked/popped bla command
        completed_bla = v.sync_old_command(testing.DummyRequest(
            method='DELETE', matchdict={'command_id': popped_bla['id']}))
        self.assertEqual(completed_bla, fetched_bla)

        # We cannot fetch the bla command after completing it
        fetched_completed_bla = v.sync_old_command(testing.DummyRequest(
            method='GET', matchdict={'command_id': popped_bla['id']}))
        self.assertEqual('No command with supplied ID',
                         fetched_completed_bla['error'])

        # The next command to pop will be oka
        popped_oka = v.sync_old_commands(testing.DummyRequest(method='PUT'))
        self.assertTrue(popped_oka['acked'])
        self.assertEqual(popped_oka['old_id'], oka['id'])

        # The next command to pop will be fra
        popped_fra = v.sync_old_commands(testing.DummyRequest(method='PUT'))
        self.assertTrue(popped_fra['acked'])
        self.assertEqual(popped_fra['old_id'], fra['id'])

        # Now the queue is empty
        response = v.sync_old_commands(testing.DummyRequest(method='PUT'))
        self.assertEqual('No commands in the queue', response['error'])
