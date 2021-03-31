from collections import namedtuple
import datetime
import json
import transaction
from uuid import uuid4

from pyramid.authorization import Allow, Everyone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Unicode,
    UnicodeText,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import asc
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import register


DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()


def gen_uuid():
    return str(uuid4())


def get_now():
    return datetime.datetime.utcnow()


old_state = namedtuple(
    'OLDState', (
        'not_synced',
        'syncing',
        'synced',
        'failed_to_sync',
    )
)(*range(4))


class DativeApp(Base):
    __tablename__ = 'dativeapp'
    uuid = Column(String(length=36), primary_key=True, default=gen_uuid)
    history_id = Column(String(length=36), default=gen_uuid, index=True)
    url = Column(Unicode(length=512))
    start = Column(DateTime, default=get_now)
    end = Column(DateTime, default=datetime.datetime.max, index=True)


class OLDService(Base):
    __tablename__ = 'oldservice'
    uuid = Column(String(length=36), primary_key=True, default=gen_uuid)
    history_id = Column(String(length=36), default=gen_uuid, index=True)
    url = Column(Text)
    start = Column(DateTime, default=get_now)
    end = Column(DateTime, default=datetime.datetime.max, index=True)


class OLD(Base):
    __tablename__ = 'old'
    uuid = Column(String(length=36), primary_key=True, default=gen_uuid)
    history_id = Column(String(length=36), default=gen_uuid, index=True)
    # suffixed to the URL of the local OLDService.url, e.g., "oka"
    slug = Column(Unicode(length=256), nullable=False, index=True)
    # human readable name, e.g., "Okanagan"
    name = Column(Unicode(length=256), nullable=False)
    # Leader is the URL of an external OLD instance that this OLD instance
    # follows and syncs with. The username and password are the credentials for
    # authenticating to the leader.
    leader = Column(Unicode(length=512))
    username = Column(Unicode(length=256))
    password = Column(Unicode(length=256))
    state = Column(Integer, default=old_state.not_synced) # see old_state above
    # setting indicates whether DativeTop should continuously and
    # automatically keep this local OLDInstance in sync with its leader.
    is_auto_syncing = Column(Boolean, default=False)
    start = Column(DateTime, default=get_now)
    end = Column(DateTime, default=datetime.datetime.max, index=True)


class SyncOLDCommand(Base):
    __tablename__ = 'syncoldcommand'
    uuid = Column(String(length=36), primary_key=True, default=gen_uuid)
    history_id = Column(String(length=36), default=gen_uuid, index=True)
    old_id = Column(Integer, ForeignKey('old.history_id'), index=True)
    acked = Column(Boolean, default=False, index=True)
    start = Column(DateTime, default=get_now, index=True)
    end = Column(DateTime, default=datetime.datetime.max, index=True)


# Dative App helper functions

DEFAULT_DATIVE_APP_URL = 'http://127.0.0.1:5678'


def serialize_dative_app(dative_app):
    return {'id': dative_app.history_id,
            'url': dative_app.url}


def get_dative_app():
    now = get_now()
    try:
        return DBSession.query(DativeApp).filter(DativeApp.end > now).one()
    except NoResultFound:
        pass
    except MultipleResultsFound:
        for app in DBSession.query(DativeApp).filter(DativeApp.end > now).all():
            app.end = now
            DBSession.add(app)
    app = DativeApp(url=DEFAULT_DATIVE_APP_URL)
    DBSession.add(app)
    DBSession.flush()
    return app


def update_dative_app(url):
    app = get_dative_app()
    now = get_now()
    app.end = now
    new_app = DativeApp(url=url,
                        history_id=app.history_id,
                        start=now)
    DBSession.add(app)
    DBSession.add(new_app)
    DBSession.flush()
    return new_app


# OLD Service App helper functions

DEFAULT_OLD_SERVICE_URL = 'http://127.0.0.1:5679'


def serialize_old_service(old_service):
    return {'id': old_service.history_id,
            'url': old_service.url}


def get_old_service():
    now = get_now()
    try:
        return DBSession.query(OLDService).filter(OLDService.end > now).one()
    except NoResultFound:
        pass
    except MultipleResultsFound:
        for old_service in DBSession.query(OLDService).filter(
                OLDService.end > now).all():
            old_service.end = now
            DBSession.add(old_service)
    old_service = OLDService(url=DEFAULT_OLD_SERVICE_URL)
    DBSession.add(old_service)
    DBSession.flush()
    return old_service


def update_old_service(url):
    old_service = get_old_service()
    now = get_now()
    old_service.end = now
    new_old_service = OLDService(url=url,
                                 history_id=old_service.history_id,
                                 start=now)
    DBSession.add(old_service)
    DBSession.add(new_old_service)
    DBSession.flush()
    return new_old_service


# OLD helper functions

def create_old(slug, name=None, leader=None, username=None, password=None,
               is_auto_syncing=False):
    existing_old = DBSession.query(OLD).filter(
        OLD.slug == slug,
        OLD.end > get_now()).first()
    if existing_old:
        raise ValueError('Slug already in use')
    name = name or slug
    old = OLD(slug=slug,
              name=name,
              leader=leader,
              username=username,
              password=password,
              is_auto_syncing=is_auto_syncing)
    DBSession.add(old)
    DBSession.flush()
    return old


def update_old(old, **kwargs):
    now = get_now()
    if old.end < now:
        raise ValueError('Cannot update an inactive OLD')
    old.end = now
    new_kwargs = {'history_id': old.history_id,
                  'start': now}
    for attr in ['slug', 'name', 'leader', 'username', 'password',
                 'state', 'is_auto_syncing']:
        new_kwargs[attr] = kwargs.get(attr, getattr(old, attr))
    new_old = OLD(**new_kwargs)
    DBSession.add(old)
    DBSession.add(new_old)
    DBSession.flush()
    return new_old


def transition_old(old, state):
    now = get_now()
    if old.end < now:
        raise ValueError('Cannot transition an inactive OLD')
    old.end = now
    new_kwargs = {'history_id': old.history_id,
                  'start': now,
                  'state': state}
    for attr in ['slug', 'name', 'leader', 'username', 'password',
                 'is_auto_syncing']:
        new_kwargs[attr] = getattr(old, attr)
    new_old = OLD(**new_kwargs)
    DBSession.add(old)
    DBSession.add(new_old)
    DBSession.flush()
    return new_old


def delete_old(old):
    old.end = get_now()
    DBSession.add(old)
    DBSession.flush()
    return old


def get_old(history_id):
    now = get_now()
    old = DBSession.query(OLD).filter(
        OLD.history_id == history_id,
        OLD.end > now
    ).one()
    return old


def get_olds():
    now = get_now()
    olds = DBSession.query(OLD).filter(
        OLD.end > now
    ).all()
    return olds


# Command helper functions

# Command state machine: enqueued -> acked -> complete
# enqueued: c.acked = False (active)
# acked:    c.acked = True  (active)
# complete: c.end   < now

def enqueue_sync_old_command(old_id):
    """Enqueue a sync-OLD! command."""
    now = get_now()
    existing_command = DBSession.query(SyncOLDCommand).filter(
        SyncOLDCommand.end > now,
        SyncOLDCommand.old_id == old_id,
    ).first()
    if existing_command:
        return existing_command
    command = SyncOLDCommand(old_id=old_id) # enqueued
    DBSession.add(command)
    DBSession.flush()
    return command


def get_sync_old_command(sync_old_command_id):
    """Get the sync-OLD! with the provided ID."""
    now = get_now()
    command = DBSession.query(SyncOLDCommand).filter(
        SyncOLDCommand.history_id == sync_old_command_id,
        SyncOLDCommand.end > now
    ).one()
    return command


def pop_sync_old_command():
    """Get the next sync-OLD! command that needs to be run, or ``None`` if there
    aren't any. Pop it from the end of the queue by acknowledging it."""
    now = get_now()
    next_command = DBSession.query(SyncOLDCommand).filter(
        SyncOLDCommand.end > now,
        SyncOLDCommand.acked.is_(False)
    ).order_by(
        asc(SyncOLDCommand.start)
    ).first()
    if not next_command:
        return None
    next_command.end = now
    new_kwargs = {'history_id': next_command.history_id,
                  'old_id': next_command.old_id,
                  'acked': True,}
    new_next_command = SyncOLDCommand(**new_kwargs)
    DBSession.add(next_command)
    DBSession.add(new_next_command)
    DBSession.flush()
    return new_next_command


def complete_sync_old_command(sync_old_command_id):
    """Update the acked sync-OLD! command to mark it as completed."""
    now = get_now()
    command = DBSession.query(SyncOLDCommand).filter(
        SyncOLDCommand.history_id == sync_old_command_id,
        SyncOLDCommand.end > now,
        SyncOLDCommand.acked.is_(True)
    ).one()
    command.end = now
    DBSession.add(command)
    DBSession.flush()
    return command
