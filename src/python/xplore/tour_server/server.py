import sys

import cherrypy

try:
    import pyor
except:
    import mock_pyor as pyor


class TourService(object):
    """Controller that produces tours based on two input parameters.

    The input parameters are expected in a JSON-encoded body, two tuples
    with longitude and latitude of the start and end location of the tour.
    """
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        params = cherrypy.request.json
        start_location = params['start_location']
        end_location = params['end_location']
        return {'waypoints': pyor.get_path(start_location, end_location)}


def run_server():
    app_conf = {
        '/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
    server_conf = {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8082,
        'log.error_file': 'error.log',
        'log.access_file': 'access.log',
        'log.screen': False
    }
    d = cherrypy.process.plugins.Daemonizer(cherrypy.engine)
    d.subscribe()
    cherrypy.config.update(server_conf)
    cherrypy.quickstart(TourService(), '/', app_conf)

if __name__ == '__main__':
    sys.exit(run_server())
