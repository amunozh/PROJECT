import json
import cherrypy


@cherrypy.expose
class scWebservice(object):
    '''
    Service Catalog MicroService class
    '''

    def GET(self, *uri, **params):

        res = None
        try:
            res = 'response from container'

        except Exception as e:
            res = str(e)
        print(res)
        if res:
            return self._responsJson(res,True)
        else:
            return self._responsJson('Bad Request', False)

    def _responsJson(self, result, success):
        ''' function to handle the format of response messages '''
        tempJson = {'result': result, 'success': success}
        return json.dumps(tempJson)

if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(scWebservice(), '/catalog.json', conf)
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8181
    cherrypy.engine.start()
    cherrypy.engine.block()
