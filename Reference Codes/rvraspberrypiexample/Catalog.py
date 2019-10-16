# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 12:49:26 2018

@author: Shuyang
"""

import cherrypy
import json
import paho.mqtt.client as paho
import requests
from Information import Info

class catalog :

    exposed = True
    obj = Info("catalog.json.conf.txt")


    def GET(self,*uri,**params) :

        if uri[0] == 'broker' :
          # get ip address and port number of the broker
            return self.obj.getBroker()

        if uri[0] == 'devices' :
          # get the information of all registered devices or one registered device
            if params['id'] == 'all' :
                return self.obj.get_allDevices()
            else :
                return self.obj.search_device(params['id'])

        if uri[0] == 'user' :
          # get the information of all registered users or one registered user
            if params['id'] == 'all' :
                return self.obj.get_allUsers()
            else :
                return self.obj.search_user(params['id'])

        if uri[0] == 'medicine' :
          # get the information of all medicines or one medicine
            if uri[1] == 'name' :
                if params['name'] == 'all' :
                    return self.obj.get_medicine()
                else :
                    return self.obj.get_medicine(params['name'])
            elif uri[1] == 'place' :
                return self.obj.get_medicineByplace(params['medicine'])

        if uri[0] == 'place' :
          # get the place of this medicine
            return self.obj.get_placeByMedicineName(params['name'])

        if uri[0] == 'schedule' :
          # get time interval of each medicine
            return self.obj.get_medicineSchedule()

        if uri[0] == 'status' :
          # get time interval of each medicine
            return self.obj.get_medicineStatus()

        if uri[0] == 'current_user':
          # Current user can be changed by pressing button
            return self.obj.get_currentUser()

        if uri[0] == 'tempth' :
          # get temperature threshold of all medicines or one medicine
            if params['name'] == 'all' :
                return self.obj.get_temp_th()
            else :
                return self.obj.get_temp_th(params['name'])

        if uri[0] == 'humith' :
          # get humidity threshold of all medicines or one medicine
            if params['name'] == 'all' :
                return self.obj.get_humi_th()
            else :
                return self.obj.get_humi_th(params['name'])

        if uri[0] == 'qty' :
          # get the current quantity of all medicines or one medicine
            if params['name'] == 'all' :
                return self.obj.get_quantity()
            else :
                return self.obj.get_quantity(params['name'])

        if uri[0] == 'pill' :
          # get pill_per_day information of all medicines or one medicine
            if params['name'] == 'all' :
                return self.obj.get_pillsPerTime()
            else :
                return self.obj.get_pillsPerTime(params['name'])

        if uri[0] == 'topic' :
         # get the mqtt-topic of the microservices /thingspeak adaptor /lED /display
         # tp = topic
            if params['tp'] == 'pc' :     # pc : pressing control
                return self.obj.get_topic_pressing_control()
            if params['tp'] == 'ts' :     # ts : time shift
                return self.obj.get_topic_time_shift()
            if params['tp'] == 'qc' :     # qc : quantity control
                return self.obj.get_topic_quantity_control()
            if params['tp'] == 'env' :     # env : environment control
                return self.obj.get_topic_env_control()
            if params['tp'] == 'tsa' :     # ts : thingspeak adaptor
                return self.obj.get_topic_thingspeak_adaptor()



    def POST(self,*uri,**params) :

        if uri[0] == 'set' :
            if uri[1] == 'broker' :
                self.obj.setBroker(params['ip'],params['port'])
                return

        if uri[0] == 'add' :
            if uri[1] == 'device' :
                self.obj.add_device(params['id'],params['ip'],
                                    params['topic'],params['resource'])
                return "insertion/update successful"
            if uri[1] == 'user' :
                self.obj.add_user(params['id'],params['name'],
                                    params['surname'],params['email'])
                return "insertion/update successful"
            if uri[1] == 'medicine' :
                msg = self.obj.add_medicine(params['user'],params['name'],int(params['init_qty']),
                                      int(params['curr_qty']),int(params['tempth']),int(params['humith']),
                                      int(params['pills']),int(params['num_times']),params['time_interval'],
                                      int(params['place']))
                if msg == None:
                    return "insertion/update successful"
                else:
                    return msg

        if uri[0] == 'status':
            if uri[1] == 'reset':
                self.obj.reset_medicineStatus()
            elif uri[1] == 'set':
                self.obj.set_medicineStatus_button(params['user'],params['medicine'],params['time'])
            return "insertion/update successful"

        if uri[0] == 'qty':
            self.obj.set_quantity(params['medicine'],params['quantity'])
            return "insertion/update successful"

        if uri[0] == 'current_user':
            self.obj.set_currentUser(params['user'])
            return "insertion/update successful"

        if uri[0] == 'new' :
            # buy new medicine due to environment reason or the quantity is not enough
            self.obj.buy_new_medicine(params['name'],params['replace'])
            topic = json.loads(self.obj.get_topic_env_control())
            sub_topic,pub_topic = topic["sub"],topic["pub"]
            pub_client = paho.Client("Catalog_pub")
            broker = json.loads(self.obj.getBroker())
            broker_ip,broker_port = broker['ip'],broker['port']
            pub_client.connect(broker_ip)
            pub_client.loop_start()
            payload = json.dumps({'medicine':params['name']})
            pub_client.publish(sub_topic,payload) 
            pub_client.disconnect()
            pub_client.loop_stop()
            del pub_client
            return "insertion/update successful"

        if uri[0] == 'topic' :
            if uri[1] == 'pc' :     # pc : pressing control
                self.obj.set_topic_pressing_control(params['sub'],params['pub'])
                return "insertion/update successful"

            if uri[1] == 'ts' :     # ts : time shift
                self.obj.set_topic_time_shift(params['pub'])
                return "insertion/update successful"

            if uri[1] == 'qc' :     # qc : quantity control
                self.obj.set_topic_quantity_control(params['sub_button'],params['sub_timeShift'],params['pub'])
                return "insertion/update successful"

            if uri[1] == 'env' :     # env : environment control
                self.obj.set_topic_env_control(params['sub'],params['pub'])
                return "insertion/update successful"

            if uri[1] == 'tsa' :     # ts : thingspeak adaptor
                self.obj.set_thingspeak_adaptor(params['channelID'],params['api_key'])
                return "insertion/update successful"



    def DELETE(self,*uri,**params) :
        if uri[0] == 'remove' :
            if uri[1] == 'devices' :
                self.obj.remove_devices(float(params['timeout']))
                return "removing successful"
            if uri[1] == 'medicine' :
                self.obj.remove_medicine(params['name'])
                return "removing successful"




if __name__=="__main__" :


    conf = {
      '/' : {
             'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
             'tools.sessions.on' :True               
            }                 
         }

    info = Info("catalog.json.conf.txt")

    info.set_catalogServer("192.168.1.26","9090")
    ip,port = info.get_catalogServer()
    broker_ip,broker_port = json.loads(info.getBroker())['ip'],json.loads(info.getBroker())['port']
    requests.post("http://"+broker_ip+":8080"+"/AddressServer/set",{'ip':ip,'port':port})
    cherrypy.tree.mount(catalog(),'/catalog.json',conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'}) 
    cherrypy.config.update({'server.socket_port': int(port)}) 
    cherrypy.engine.start()
    cherrypy.engine.block()











