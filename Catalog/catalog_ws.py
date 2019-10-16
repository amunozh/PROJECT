import catalog
import os
import cherrypy
import json
import socket
import requests
'''
Exposing catalog.json web service
'''
cwd = os.getcwd()

class index:
    exposed = True

    def __init__(self):
        self.mycatalog = catalog.catalog(os.path.join(cwd, "catalog.json"))
        self.mycatalog.update()

    def GET(self, *uri, **params):#TODO:show services
        if uri:
            if uri[0] == 'broker': #TODO:SHOW_SERVICES
                response = self.mycatalog.broker()
            elif uri[0] == 'show_devices':
                print("hello")
                response = self.mycatalog.devices()
            elif uri[0] == 'show_users':
                response = self.mycatalog.users()
            elif uri[0] == 'search_user':
                response = self.mycatalog.search_user(params['ID'])
            elif uri[0] == 'search_device':
                response = self.mycatalog.search_device(params['ID'])
            else:
                response = 0
        else:
            response = 0

        return (json.dumps(response))

    def POST(self, *uri, **params):
        if uri:
            if uri[0] == 'add_device':#TODO:check it is not in the catalog.
                #To add device url like IP:port/catalog.json/add_device?ID=ID_dev&end_point=[REST, MQTT]&resources=[ID_Reousrce]
                response = self.mycatalog.add_device(params['ID'], params['end_point'], params['resources'])
                # To add user url like IP:port/catalog.json/add_user?name=user_name&surname=user_surname&telegram=telegram_account
            elif uri[0] == 'add_user':
                response = self.mycatalog.add_user(params['name'], params['surname'], params['telegram'])

            elif uri[0] == 'add_service':
                response = self.mycatalog.add_service(params['ID'], params['end_point'], params['resources'])
            else:
                response = 0
        else:
            response = 0

        return(json.dumps(response))

    def PUT(self, *uri, **params):
        if uri:
            if uri[0] == 'refresh':
                response = self.mycatalog.refresh(params['ID'])
                return("Updated") #TODO: test puts
            elif uri[0] == 'echo': #Use this resource to make test
                return(params['test'])
            else:
                response = 0
        else:
            response = 0

        return (str(response))

    def DELETE(self):
        pass


if __name__=="__main__" :

    conf = {'/'
            : {'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
               'tools.sessions.on': True, }}

    cherrypy.tree.mount(index(), '/catalog', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8282})

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    print(IPAddr)
    r = requests.post("http://" + IPAddr + ":8181" + "/address_manager/set", {'ip': IPAddr, 'port': 8282})
    print(r)

    cherrypy.engine.start()
    cherrypy.engine.block()