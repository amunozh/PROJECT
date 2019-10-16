# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:51:12 2019

@author: Miguel
"""

import string 
import cherrypy 
import json


class PalindromeWS(object): 
	exposed = True 

	def __init__(self):
		self.palindrome = Palindrome()

	def GET (self, *uri): 
		if len(uri)>0:
			isPalindrome = self.palindrome.isPalindrome(uri[0])
			response = {"Request": uri[0], "Reply":isPalindrome}
			responseJson = json.dumps(response)
		else:
            
			responseJson = json.dumps({"error": "wrong number of parameters"})
		return responseJson
    
    
	def PUT(self, *uri, **params):
		if uri:
		 if uri[0] == 'echo':
                         response = cherrypy.request.body.read().decode('utf-8')
		 else:
                             response = 0
		else:
                        response = 0

		return (str(response))

    
class Palindrome(object):
   def __init__(self):
		#nothing to do
    pass
   def isPalindrome(self,word):
    if word=="ArduinoHR":
        Topic='Miguel1096/test/HR'
    elif word=="Check":
        Topic='OK'
    else:
        Topic='OFF'
    return (Topic)

if __name__ == '__main__':
    conf = {'/'
            : {'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
               'tools.sessions.on': True, }}

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.tree.mount (PalindromeWS(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()

