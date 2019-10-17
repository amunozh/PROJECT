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
                response = self.mycatalog.devices()
            elif uri[0] == 'show_services':
                response = self.mycatalog.services()
            elif uri[0] == 'show_users':
                response = self.mycatalog.users()
            elif uri[0] == 'search_user':
                data = json.loads(params['json_msg'])
                response = self.mycatalog.search_user(data['ID'])
            elif uri[0] == 'search_device':
                data = json.loads(params['json_msg'])
                response = self.mycatalog.search_device(data['ID'])
            else:
                response = 0
        else:
            response = 0

        return (json.dumps(response))

    def POST(self, *uri, **params):
        if uri:
            if uri[0] == 'add_device':#TODO:check it is not in the catalog.
                received_data = params['json_msg']
                data = received_data.replace("'",'"')
                print(data)
                data = json.loads(data)
                response = self.mycatalog.add_device(data['ID'], data['end_point'], data['resources'])
                # To add user url like IP:port/catalog.json/add_user?name=user_name&surname=user_surname&telegram=telegram_account
            elif uri[0] == 'add_user':
                data = json.loads(params['json_msg'])
                response = self.mycatalog.add_user(data['name'], data['surname'], data['telegram'])

            elif uri[0] == 'add_service':
                data = json.loads(params['json_msg'])
                response = self.mycatalog.add_service(data['ID'], data['end_point'], data['resources'])
            else:
                response = 0
        else:
            response = 0

        return(json.dumps(response))

    def PUT(self, *uri, **params):
        if uri:
            if uri[0] == 'refresh':
                data = json.loads(params['json_msg'])
                response = self.mycatalog.refresh(data['ID'])
                return("Updated") #TODO: test puts
            elif uri[0] == 'echo': #Use this resource to make test
                data = json.loads(params['json_msg'])
                return(data['test'])
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
    data = json.dumps({'ip': IPAddr, 'port': 8282})
    r = requests.post("http://" + IPAddr + ":8181" + "/address_manager/set?json_msg=" + data)
    print(r)

    cherrypy.engine.start()
    cherrypy.engine.block()