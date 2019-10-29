# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 22:34:06 2017

@author: Andres Hernando
"""



import cherrypy
import socket
import json
from os.path import abspath
from cherrypy import tools
import requests

#Rest architecture class
class index:    
    exposed=True
    cherrypy.tools.json_in()
    def GET (self,*uri,**params):
        return (open("./freeboard/index.html"))
    def POST (self,*uri,**params):
        data=params['json_string']
        print(data)
        with open('./freeboard/dashboard/dashboard.json','w') as f:
            f.write(data)
        
    def PUT (self, *uri, **params):
        pass
    
    def DELETE (self):
        pass
        

if __name__ == '__main__':

    Port = 9292
    conf = {'/'
        : {'tools.staticdir.on': True,
            'tools.staticdir.dir': abspath('./freeboard'),
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
           'tools.sessions.on': True,}}

    cherrypy.tree.mount(index(), '/catalog', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': Port})

    IP_addres_man = "192.168.1.123"
    Port_address_man = str(8585)
    response = requests.get("http://" + IP_addres_man + ":" + Port_address_man + "/address_manager/get")
    r = response.content.decode('utf-8')
    jr = json.loads(r)

    catalogIP = jr['ip']
    catalogPort = str(jr['port'])

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    register_data = json.dumps({'ID': "dashboard01" , 'end_point': [None, IPAddr +":"+str(Port)+"/"], 'resources': ['dashboard']})
    response = requests.post(
        "http://" + catalogIP + ":" + catalogPort + "/catalog/add_service?json_msg=" + register_data)


    print('Dashboard registered succesfully')

    cherrypy.tree.mount (index(),'/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
    