import os
import cherrypy
import json
'''
Exposing address manager web service: allows to find the catalog.json address
'''
cwd = os.getcwd()



class index:
    exposed = True
    def __init__(self):
        pass

    def GET(self,*uri,**params):
        if uri:
            if uri[0] == 'get':
                file = open(os.path.join(cwd, "addresses"))
                json_file = json.load(file)
                address = json.dumps({'ip':json_file['ip'],'port':json_file['port']})
                file.close()
                return address

    def POST(self,*uri,**params):
        if uri[0] == 'set':
            file = open("addresses","w+")
            data = params['json_msg']
            address = json.dumps({'ip':data['ip'],'port':data['port']})
            file.write(address)
            file.close()
            return "Update Successfully"


if __name__ == '__main__':

    conf = {
            '/':{
                    'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                    'tools.sessions.on':True
                }
            }
    cherrypy.tree.mount(index(),"/address_manager",conf)
    cherrypy.config.update({'server.socket_host':'0.0.0.0'})
    cherrypy.config.update({'server.socket_port':8181})
    cherrypy.engine.start()
    cherrypy.engine.block()