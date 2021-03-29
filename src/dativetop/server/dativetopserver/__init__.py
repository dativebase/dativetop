from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession, Base
import dativetopserver.views as views


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('dativetopserver.cors')
    config.add_cors_preflight_handler()
    config.add_route('append-only-log', '/')
    config.add_view(views.append_only_log,
                    route_name='append-only-log',
                    renderer='json')
    config.scan()
    return config.make_wsgi_app()
