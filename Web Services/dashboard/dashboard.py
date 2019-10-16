# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 22:34:06 2017

@author: Andres Hernando
"""



import cherrypy

import json
from os.path import abspath
from cherrypy import tools

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

    
    conf = {'/'
        : {'tools.staticdir.on': True,
            'tools.staticdir.dir': abspath('./freeboard'),
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
           'tools.sessions.on': True,}}

    cherrypy.tree.mount(index(), '/catalog', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 9292})

    cherrypy.tree.mount (index(),'/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
    