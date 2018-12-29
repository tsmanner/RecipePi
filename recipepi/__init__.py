from pyramid.config import Configurator
from wsgiref.simple_server import make_server


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator() as config:
        config.include('pyramid_jinja2')
        config.add_route('recipe', '/recipe')
        # config.add_view(hello_world, route_name='root')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()
