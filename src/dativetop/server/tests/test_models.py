import unittest
import transaction

from pyramid import testing


def _initTestingDB():
    from sqlalchemy import create_engine
    from dativetopserver.models import (
        Base,
        DativeApp,
        DBSession,
        OLD,
        OLDService,
        SyncOLDCommand,
    )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession


class ModelsTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_dative_app_api(self):
        import dativetopserver.models as m
        self.assertEqual([], self.session.query(m.DativeApp).all())
        app = m.get_dative_app()
        self.assertEqual([app], self.session.query(m.DativeApp).all())
        updated_app = m.update_dative_app('app-url-updated')
        final_url = 'http://localhost:5679'
        finalized_app = m.update_dative_app(final_url)
        apps = self.session.query(m.DativeApp).all()
        now = m.get_now()
        self.assertEqual(3, len(set([a.url for a in apps])),
                         'expected 3 distinct app URLs')
        self.assertEqual(3, len(set([a.uuid for a in apps])),
                         'expected 3 distinct app IDs')
        self.assertEqual(1, len([a for a in apps if a.end > now]),
                         'expected 1 active app')
        self.assertEqual(2, len([a for a in apps if a.end < now]),
                         'expected 2 inactive apps')
        self.assertEqual(final_url, [a for a in apps if a.end > now][0].url,
                         'expected final URL for active app')
        self.assertEqual(final_url, finalized_app.url,
                         'expected final URL for returned active app')

    def test_old_service_api(self):
        import dativetopserver.models as m
        self.assertEqual([], self.session.query(m.OLDService).all())
        old_service = m.get_old_service()
        self.assertEqual([old_service], self.session.query(m.OLDService).all())
        updated_old_service = m.update_old_service('service-url-updated')
        final_url = 'http://localhost:5673'
        finalized_old_service = m.update_old_service(final_url)
        old_services = self.session.query(m.OLDService).all()
        now = m.get_now()
        self.assertEqual(3, len(set([a.url for a in old_services])),
                         'expected 3 distinct old service URLs')
        self.assertEqual(3, len(set([a.uuid for a in old_services])),
                         'expected 3 distinct old service IDs')
        self.assertEqual(1, len([a for a in old_services if a.end > now]),
                         'expected 1 active old service')
        self.assertEqual(2, len([a for a in old_services if a.end < now]),
                         'expected 2 inactive old service')
        self.assertEqual(final_url, [a for a in old_services if a.end > now][0].url,
                         'expected final URL for active old service')
        self.assertEqual(final_url, finalized_old_service.url,
                         'expected final URL for returned active old service')

    def test_old_api(self):
        import dativetopserver.models as m
        from sqlalchemy.orm.exc import NoResultFound
        self.assertEqual([], self.session.query(m.OLD).all())

        # Create an initial OLD, supplying just the slug
        old1 = m.create_old('oka')
        old_service = m.get_old_service()
        self.assertEqual('oka', old1.slug)
        self.assertEqual('oka', old1.name)
        self.assertIsNone(old1.leader)
        self.assertIsNone(old1.username)
        self.assertIsNone(old1.password)
        self.assertFalse(old1.is_auto_syncing)
        self.assertEqual(m.old_state.not_synced, old1.state)

        # Create a second OLD, supplying everything
        old2 = m.create_old('bla',
                           name='Blackfoot',
                           leader='https://do.onlinelinguisticdatabase.org/blaold',
                           username='someuser',
                           password='somepassword',
                           is_auto_syncing=True)
        self.assertEqual('bla', old2.slug)
        self.assertEqual('Blackfoot', old2.name)
        self.assertEqual('https://do.onlinelinguisticdatabase.org/blaold',
                         old2.leader)
        self.assertEqual('someuser', old2.username)
        self.assertEqual('somepassword', old2.password)
        self.assertTrue(old2.is_auto_syncing)
        old2_history_id = old2.history_id

        # Update the second OLD
        new_old2 = m.update_old(old2, leader='abc')
        self.assertEqual('abc', new_old2.leader)
        for attr in ['slug', 'name', 'username', 'password', 'is_auto_syncing']:
            self.assertEqual(getattr(old2, attr), getattr(new_old2, attr))
        olds = self.session.query(m.OLD).all()
        self.assertEqual(3, len(olds))
        self.assertEqual(2, len([o for o in olds if o.end > m.get_now()]))
        self.assertEqual(2, len(m.get_olds()))
        self.assertEqual(new_old2, m.get_old(old2_history_id))

        # Attempting to create an OLD with the slug of an existing OLD will throw
        try:
            m.create_old(new_old2.slug)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        # Delete the second OLD
        deleted_old2 = m.delete_old(new_old2)
        self.assertGreater(m.get_now(), deleted_old2.end)
        self.assertEqual(1, len(m.get_olds()))
        try:
            m.get_old(old2_history_id)
        except Exception as e:
            self.assertIsInstance(e, NoResultFound)

        # After deleting the second OLD, we can reuse its slug.
        # Let's transition it through some plausible state transitions.
        blaold = m.create_old(new_old2.slug)
        self.assertEqual(m.old_state.not_synced,
                         m.get_old(blaold.history_id).state)
        blaold_syncing = m.transition_old(blaold, m.old_state.syncing)
        self.assertEqual(m.old_state.syncing,
                         m.get_old(blaold.history_id).state)
        blaold_synced = m.transition_old(blaold_syncing, m.old_state.synced)
        self.assertEqual(m.old_state.synced,
                         m.get_old(blaold.history_id).state)
        blaold_not_synced = m.transition_old(blaold_synced,
                                             m.old_state.not_synced)
        self.assertEqual(m.old_state.not_synced,
                         m.get_old(blaold.history_id).state)

        # We cannot transition a deactivated OLD
        try:
            m.transition_old(blaold_synced, m.old_state.not_synced)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        # Transition a new OLD through a "sync failed" flow
        zinc_old = m.create_old('zinc')
        self.assertEqual(m.old_state.not_synced,
                         m.get_old(zinc_old.history_id).state)
        zinc_old_syncing = m.transition_old(zinc_old, m.old_state.syncing)
        self.assertEqual(m.old_state.syncing,
                         m.get_old(zinc_old.history_id).state)
        zinc_old_failed_to_sync = m.transition_old(
            zinc_old_syncing, m.old_state.failed_to_sync)
        self.assertEqual(m.old_state.failed_to_sync,
                         m.get_old(zinc_old.history_id).state)
        zinc_old_not_synced = m.transition_old(zinc_old_failed_to_sync,
                                               m.old_state.not_synced)
        self.assertEqual(m.old_state.not_synced,
                         m.get_old(zinc_old.history_id).state)

    def test_sync_old_command_api(self):
        import dativetopserver.models as m
        from sqlalchemy.orm.exc import NoResultFound

        # The queue is initially empty
        self.assertIsNone(m.pop_sync_old_command())

        # Create 3 OLDs and a sync command for the second.
        old1 = m.create_old('one')
        old2 = m.create_old('two')
        old3 = m.create_old('three')
        cmd1 = m.enqueue_sync_old_command(old2.history_id)
        self.assertFalse(cmd1.acked)
        self.assertGreater(cmd1.end, m.get_now())
        self.assertEqual(cmd1.old_id, old2.history_id)
        self.assertIs(cmd1, m.get_sync_old_command(cmd1.history_id))

        # Trying to enqueue a sync command for the same OLD again will just
        # return the existing active command.
        cmd1_clone = m.enqueue_sync_old_command(old2.history_id)
        self.assertIs(cmd1, cmd1_clone)

        # Let's pop the command, expecting that to ACK it
        acked_cmd1 = m.pop_sync_old_command()
        self.assertTrue(acked_cmd1.acked)
        self.assertGreater(acked_cmd1.end, m.get_now())
        self.assertEqual(acked_cmd1.old_id, old2.history_id)
        self.assertIsNone(m.pop_sync_old_command())

        # Trying to enqueue a sync command for the same OLD again will again
        # just return the existing active acked command.
        cmd1_clone2 = m.enqueue_sync_old_command(old2.history_id)
        self.assertIs(acked_cmd1, cmd1_clone2)

        # Pretend we're a worker marking the command as complete
        completed_cmd1 = m.complete_sync_old_command(acked_cmd1.history_id)
        self.assertLess(acked_cmd1.end, m.get_now())

        # Create three commands and expect to pop them in FIFO order
        m.enqueue_sync_old_command(old2.history_id)
        m.enqueue_sync_old_command(old3.history_id)
        cmd = m.enqueue_sync_old_command(old1.history_id)
        self.assertEqual(old2.history_id, m.pop_sync_old_command().old_id)
        self.assertEqual(old3.history_id, m.pop_sync_old_command().old_id)
        self.assertEqual(old1.history_id, m.pop_sync_old_command().old_id)
        self.assertIsNone(m.pop_sync_old_command())

        # Cannot get a completed command
        self.assertEqual(cmd.history_id,
                         m.get_sync_old_command(cmd.history_id).history_id)
        m.complete_sync_old_command(cmd.history_id)
        try:
            m.get_sync_old_command(cmd.history_id)
        except Exception as e:
            self.assertIsInstance(e, NoResultFound)
