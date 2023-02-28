
from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    # config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.include('.routes')
    config.include('.models')
    config.scan()
    return config.make_wsgi_app()