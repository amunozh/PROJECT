import os
import cherrypy
import json
import socket
import requests
'''
Exposing DataBase Web Service
'''
cwd = os.getcwd()

class DBWS(object):
    exposed = True

    def __init__(self):
        self.filename = os.path.join(cwd, "Datalist.json")
        file = open(self.filename, 'r')  # open the file for reading it
        self.database = json.load(file)  # read the file and convert to json
        file.close()


    def GET(self, *uri, **params):
        if uri:
            if uri[0] == 'patient':
               for pac in self.database['patients']:
                    if pac['ID'] == params['ID']:
                        response = {'ID': params['ID'], 'data': pac['ID']['data'][0]}
                        return json.dumps(response)
                    else:
                        response = {"message": "ID does not exists"}
            elif uri[0] == 'all_patients':
                response = self.database['patients']
            else:
                response = 0
        else:
            response = 0

        return (json.dumps(response))

    def POST(self, *uri, **params):
        if uri:
            if uri[0] == 'update_DB':
                received_data = params['json_msg']
                data = received_data.replace("'",'"')
                print(data)
                self.database = json.loads(data)
                file = open(os.path.join(cwd, "Datalist.json"), 'r+')
                file.seek(0)
                file.write('{"patients":')
                file.write(json.dumps(self.database))
                file.write("}")
                file.truncate()
                file.close()

                response = {"Messagge":"DataBase Updated"}
                # To add user url like IP:port/catalog.json/add_user?name=user_name&surname=user_surname&telegram=telegram_account
            else:
                response = 0
        else:
            response = 0

        return(json.dumps(response))

    def PUT(self, *uri, **params):
        pass

    def DELETE(self):
        pass


if __name__=="__main__" :

    conf = {'/'
            : {'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
               'tools.sessions.on': True, }}

    cherrypy.tree.mount(DBWS(), '/database', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8383})

    DBWSPort = '8383'
    hostname = socket.gethostname()
    #IPAddr = socket.gethostbyname(hostname)
    IPAddr = '192.168.1.122'
    print(IPAddr)
    PortAddr='8585'
    # Contact to Address Manager to get the Catalog IP and Port
    response = requests.get("http://" + IPAddr + ":" + PortAddr + "/address_manager/get")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)
    IPCat = jr['ip']
    PortCat = str(jr['port'])

    # Contact to Catalog to Register as Service
    direc=str("http://" + IPAddr + ":" + DBWSPort + "/database/")
    aux = json.dumps({'ID': 'DataBase', 'end_point': [None,direc], 'resources': ['DataBase']})
    response = requests.post("http://" + IPCat + ":" + PortCat + "/catalog/add_service?json_msg=" + aux)
    r = response.content.decode('utf-8')
    print(r)

    response = requests.get("http://" + IPCat + ":" + PortCat + "/catalog/broker")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)
    IPBroker = jr['ip']
    PortBroker = jr['port']

    cherrypy.engine.start()
    cherrypy.engine.block()