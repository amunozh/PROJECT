import json
import cherrypy
import sys
from core import dbconnector_sc as sc
from core import dbconnector_an as an
from core import dbconnector_pl as pl
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

class platformWebService(object):
    '''
    Platform MicroService class
    API Calls:
        - GET   Retreive List of Houses
        - GET   Retreive Sensor Info
        - GET   Retreive Sensors List
        - POST  Update Sensor
        - POST  User Login
        - PUT   Add Sensor
        - PUT   Add User
        - PUT   Add New House
        - PUT   Add Existing House
    '''
    exposed = True

    def __init__(self):
        # self.dbclient = MongoClient()
        # self.db = self.dbclient.iotsys
        self.sc = pl.platformDbConnector()
    def GET(self, *uri, **params):
        '''
        - Name                  URL               Params
        - Retreive List of houses:    /houses     user_id
        - Retreive Sensor Info	    /sensor       sensor_id , select=[all,settings]
        - Retreive house sensors:	/house/sensors          house_id
        - Retreive Profiles list:   /profiles   None
        '''
        res = None
        error_msg = None
        try:
            if uri[0] == 'houses':
                user_id = params['user_id']
                res = self.sc.get_houses(user_id)
            elif uri[0] == 'sensors':
                sens_id = params['sensor_id']
                res = self.sc.get_sensor_settings(sens_id)
            elif uri[0] == 'house' and uri[1] == 'sensors':
                house_id = params['house_id']
                res = self.sc.get_sensors(house_id)
            elif uri[0] == 'profiles':
                res = self.sc.get_profiles()
        except Exception as e:
            res = None
            error_msg = str(e)
        if res:
            print(res)
            return res
        else:
            print(error_msg)
            return self._responsJson('Wrong request: ' + str(error_msg), False)

    def PUT(self, *uri, **params):
        res = None
        error_msg = None
        try:
            if uri[0] == 'houses' and uri[1] == 'new':
                tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                house_name = tempJson['house_name']
                user_id = tempJson['user_id']
                res = self.sc.add_house(user_id, house_name)
            if uri[0] == 'houses' and uri[1] == 'existing':
                tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                house_id = tempJson['house_id']
                user_id = tempJson['user_id']
                res = self.sc.add_house_user(user_id, house_id)
            elif uri[0] == 'sensors':
                tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                sensor_id = tempJson['sens_id']
                sensor_name = tempJson['sens_name']
                house_id = tempJson['house_id']
                profile_id = tempJson['prof_id']
                res = self.sc.add_sensor(house_id, sensor_id, sensor_name,profile_id)
            elif uri[0] == 'users':
                tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                print(tempJson)
                user_name = tempJson['user_name']
                pwd = tempJson['pwd']
                res = self.sc.add_user(user_name, pwd)
        except Exception as e:
            res = None
            error_msg = str(e)
        if res:
            return res
        else:
            return self._responsJson('wrong request: ' + error_msg, False)

    def POST(self, *uri, **params):
        res = None
        error_msg = None
        try:
            # Cherry py doesn't support receiving json by GET
            # the user authentication is done by POST method
            if uri[0] == 'userAuth':
                tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                user_name = tempJson['user_name']
                pwd = tempJson['pwd']
                res = self.sc.user_sign_in(user_name, pwd)
                print(res)
            elif uri[0] == 'houses':
                tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                house_id = tempJson['house_id']
                user_id = tempJson['user_id']
                res = self.sc.add_house_user(user_id, house_id)
            elif uri[0] == 'sensors':
                tempJson = json.loads(cherrypy.request.body.read().decode('utf-8'))
                sens_id = tempJson['sens_id']
                sens_name = tempJson['sens_name']
                sens_settings = tempJson['sens_settings']
                res = self.sc.update_sensor(sens_id, sens_name, sens_settings)
        except Exception as e:
            res = None
            error_msg = str(e)
        if res:
            print(res)
            return res
        else:
            print(error_msg)
            return self._responsJson('wrong Request' + error_msg, False)

    def _responsJson(self, result, success):
        tempJson = {'result': result, 'success': success}
        return json.dumps(tempJson)

class analyticsWebService(object):
    '''
    Anaylitcs Microservice Class
    '''
    exposed = True

    def __init__(self):
        self.sc = an.analyticsDbConnector()

    def GET(self, *uri, **params):
        """ GET URL uri parameters """
        #  Can be managed as an array
        print('in get')
        res = None
        try:
            if uri and 'sensor_id' in params and 'type' in params:
                sens_id = params['sensor_id']
                period = uri[0]
                sens_type = params['type']
                if period == 'day':
                    res = self.sc.get_data_day_hour(sens_id, sens_type)
                    print(res)
                elif period == 'week':
                    res = self.sc.get_data_week(sens_id, sens_type)
                elif period == 'month':
                    res = self.sc.get_data_month(sens_id, sens_type)
        except Exception as e:
            # res = self.sc._responsJson('Cannot get data', False)
            res = self.sc._responsJson(str(e), False)
        if res:
            return res.encode('utf8')
        else:
            return self.sc._responsJson('Wrong Request', False)




if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(scWebservice(), '/catalog.json', conf)
    cherrypy.tree.mount(analyticsWebService(), '/analytics',conf)
    cherrypy.tree.mount(platformWebService(), '/platform',conf)
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8484
    cherrypy.engine.start()
    cherrypy.engine.block()
