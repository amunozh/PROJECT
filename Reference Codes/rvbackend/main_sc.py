import json
import cherrypy
import sys
from core import dbconnector_sc as sc
from core import iotDevice as sd


@cherrypy.expose
class scWebservice(object):
    '''
    Service Catalog MicroService class
    API Calls:
        - GET   Retreive services 
        - GET   Check if device is registered
        - GET   Retreive device
        - PUT   Register device
        - POST  Update device
    '''
    def __init__(self):
        self.sc = sc.serviceCatalog()

    def GET(self, *uri, **params):
        '''
        - Name                  URL               Params
        - Check device regs:    /device/status     dev_id
        - Retreive device:	    /device/info       dev_id 
        - Retreive services:	/services          None
        - Retreive ext sensor: /house/ext          dev_id
        '''
        res = None
        try:
            if uri[0] == 'device' and uri[1] == 'status' and len(uri) == 2:
                # Check if device is registered
                device_id = str(params['dev_id'])
                print(uri)
                res = self.sc.check_device(device_id)
            elif uri[0] == 'device' and uri[1] == 'info' and len(uri) == 2:
                # Get device information
                device_id = str(params['dev_id'])
                print(device_id)
                res = self.sc.get_device(device_id)
            elif uri[0] == 'services':
                res = self.sc.get_services()
            elif uri[0] == 'house' and uri[1] == 'ext' and len(uri) == 2:
                device_id = str(params['dev_id'])
                res = self.sc.get_house_ext(device_id)
                print(res)
 
        except Exception as e:
            print(e)
            res = str(e)
        if res:
            return res
        else:
            return self._responsJson('Bad Request', False)

    def PUT(self, *uri, **params):
        '''
        - Register a device:
            - URL: /device/
            - Data Params:
                {
                    "dev_id":"SS12",
                    "dev_type":"int/ext",
                    "resources":[{}],
                    "endpoints":[{}]
                    }
            - Success Return
                {'result':'successfully registerd','success':true}
        '''
        res = None
        try:
            if uri[0] == 'device':
                # device_type = str(uri[1])
                try:
                    tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                    print(tempJson)
                    tempDevice = sd.iotDevice()
                    tempDevice.fromJson(tempJson)
                    res = self.sc.add_device(tempDevice, act=True)
                    print(res)
                except Exception as e:
                    res = self.sc._responsJson('Cannot add device:' + e, False)
        except Exception as e:
            res = None
        if res:
            return res
        else:
            return self._responsJson('Bad Request', False)

    def POST(self, *uri, **params):
        '''
        - Update device:
            - URL: /device/
                - Data Params:
                    {
                        "dev_id":"SS12",
                        "dev_type":"int/ext",
                        "resources":[{}],
                        "endpoints":[{}]
                        }
                - Success Return
                    {'result':'successfully registerd','success':true}

        '''
        res = None
        try:
            if uri[0] == 'device':
                try:
                    tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                    tempDevice = sd.iotDevice()
                    tempDevice.fromJson(tempJson)
                    res = self.sc.add_device(tempDevice, False)
                except Exception as e:
                    res = self.sc._responsJson('Cannot update device: '+str(e), False)
        except Exception as e:
            res = None
        if res:
            return res
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
