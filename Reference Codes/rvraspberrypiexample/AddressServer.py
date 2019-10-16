#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  8 12:34:02 2018

@author: pi
"""

import cherrypy
import json

class AddressServer:
    # this web server is used for getting IP address and port of catalog.json service
    # because the catalog.json server could be replaced with another one.
    # (for flexibility)
    exposed = True

    def GET(self,*uri,**params):
        if uri[0] == 'get':
            file = open("address_catalog.txt","r")
            json_file = json.load(file)
            address = json.dumps({'ip':json_file['ip'],'port':json_file['port']})
            file.close()
            return address

    def POST(self,*uri,**params):
        if uri[0] == 'set':
            file = open("address_catalog.txt","w+")
            address = json.dumps({'ip':params['ip'],'port':params['port']})
            file.write(address)
            file.close()
            return "update successfully"


if __name__ == '__main__':

    conf = {
            '/':{
                    'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                    'tools.sessions.on':True
                }
            }
    cherrypy.tree.mount(AddressServer(),"/AddressServer",conf)
    cherrypy.config.update({'server.socket_host':'0.0.0.0'})
    cherrypy.config.update({'server.socket_port':8080})
    cherrypy.engine.start()
    cherrypy.engine.block()


























