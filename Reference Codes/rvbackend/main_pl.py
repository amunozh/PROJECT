import cherrypy
import json
from pymongo import MongoClient
import datetime
from datetime import timedelta
import time
from core import dbconnector_pl as pl

@cherrypy.expose
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
        self.dbclient = MongoClient()
        self.db = self.dbclient.iotsys
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


if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    cherrypy.tree.mount(platformWebService(), '/platform', conf)
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8080
    cherrypy.engine.start()
    cherrypy.engine.block()
