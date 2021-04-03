from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession, Base
import dativetopserver.views as v


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_tm')
    config.include('dativetopserver.cors')
    config.add_cors_preflight_handler()

    config.add_route('old-service', '/old_service')
    config.add_view(v.old_service,
                    route_name='old-service',
                    renderer='json')

    config.add_route('dative-app', '/dative_app')
    config.add_view(v.dative_app,
                    route_name='dative-app',
                    renderer='json')

    config.add_route('old_state', '/olds/{old_id}/state')
    config.add_view(v.old_state,
                    route_name='old_state',
                    renderer='json')

    config.add_route('old', '/olds/{old_id}')
    config.add_view(v.old,
                    route_name='old',
                    renderer='json')

    config.add_route('olds', '/olds')
    config.add_view(v.olds,
                    route_name='olds',
                    renderer='json')

    config.add_route('sync_old_command', '/sync_old_commands/{command_id}')
    config.add_view(v.sync_old_command,
                    route_name='sync_old_command',
                    renderer='json')

    config.add_route('sync_old_commands', '/sync_old_commands')
    config.add_view(v.sync_old_commands,
                    route_name='sync_old_commands',
                    renderer='json')

    config.scan()
    return config.make_wsgi_app()
