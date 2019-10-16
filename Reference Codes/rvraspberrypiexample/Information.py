# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 13:02:34 2018

@author: Shuyang
"""

import json
from time import gmtime, strftime
import time



class Info :

  ###############  Basic functions  #################


    def __init__(self,json_file) :
        self.json_data = open(json_file)
        self.file_name = json_file
        self.data = json.load(self.json_data)
        self.json_data.close()


    def overwrite(self) :
        self.cahce = json.dumps(self.data)
        self.json_data= open(self.file_name,'w')
        self.json_data.write(self.cahce)
        self.json_data.close()


    def get_lastUpdate_info(self) :
        return json.dumps({"time":self.data['last_update']['time'],"info":self.data['last_update']['info']})


    def set_catalogServer(self,ip="0.0.0.0",port="9090") :
        self.data['server']['ip'] = ip
        self.data['server']['port'] = port
        self.data['last_update']['info'] = "Update the information of broker"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()

    def get_catalogServer(self) :
        return self.data['server']['ip'],self.data['server']['port']


  ############### functions about pi service,Broker,device,user and medicine ###############

    def setBroker(self,ip_broker,port_broker) : 
        self.data['broker']['ip'] = ip_broker
        self.data['broker']['port'] = port_broker
        self.data['last_update']['info'] = "Update the information of broker"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def getBroker(self) :
        return json.dumps({"ip":self.data['broker']['ip'],"port":self.data['broker']['port']})


    def add_device(self,device_id,device_ip,mqtt_topic,resources):
        for e in self.data['devices']:
            if e['ID'] == device_id :
                e['endpoints']['ip'] = device_ip
                e['endpoints']['mqtt_topic'] = mqtt_topic
                e['resources'] = resources
                e['timestamp'] = time.time()
                self.data['last_update']['info'] = "Update the information of device"
                self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
                self.overwrite()
                return

        new_device = {'ID':device_id,'endpoints':{'ip':device_ip,'mqtt_topic':mqtt_topic},
                      'resources':resources,'timestamp':time.time()}
        self.data['devices'].append(new_device)
        self.data['last_update']['info'] = "Add a new device"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def get_allDevices(self) :
        return json.dumps({'devices':self.data['devices']})

    def search_device(self,search_id) :
        for e in self.data['devices'] :
            if e['ID'] == search_id:
                return json.dumps({'devices':e})
        return None             # no device with this ID


    def add_user(self,user_id,name,surname,email) :
        for e in self.data['User'] :
            if e['ID'] == user_id :
                e['name'] = name
                e['surname'] = surname
                e['email'] = email
                self.data['last_update']['info'] = "Update the information of user"
                self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
                self.overwrite()
                return

        new_user = {'ID':user_id,'name':name,'surname':surname,'email':email}
        self.data['User'].append(new_user)
        self.data['last_update']['info'] = "Add a new user"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def get_allUsers(self) :
        return json.dumps({"user":self.data['User']})


    def search_user(self,search_id) :
        for e in self.data['User'] :
            if e['ID'] == search_id:
                return json.dumps({'user':e})
        return None             # no user with this ID


    def remove_devices(self,timeout):
        for e in self.data['devices'] :
            if time.time()-e['timestamp'] > timeout :
                self.data['devices'].remove(e)
        self.overwrite()
        return


    def add_medicine(self,user,medicine_name,init_quantity,curr_quantity,temp_th,humi_th, \
                     quantity_per_time,num_times,time_interval,place) :
       # checking if the medicine has already been registered
        if self.data['place'][str(place)] != 'NULL' and medicine_name != self.data['place'][str(place)]:
            return "place has already been registered"
        for e in self.data['medicine'] :
            if e['name'] == medicine_name :
                old_place = e['place']*1
                self.data['place'][str(old_place)] = 'NULL'
                e['initial_quantity'] = init_quantity
                e['current_quantity'] = curr_quantity
                e['temperature_threshold'] = temp_th
                e['humidity_threshold'] = humi_th
                e['pills_per_time'] = quantity_per_time
                e['place'] = place              # the place in box (e.g. 1,2,3,4 etc.)
                self.data['place'][str(place)] = medicine_name
                self.set_medicineSchedule(user,medicine_name,num_times,time_interval)
                self.set_medicineStatus(user,medicine_name,num_times)
                self.data['last_update']['info'] = "Update the information of medicine"
                self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
                self.overwrite()
                return
        new_medicine = {'name':medicine_name,'initial_quantity':init_quantity,'current_quantity':curr_quantity,
                        'temperature_threshold':temp_th,'humidity_threshold':humi_th, \
                        'pills_per_time':quantity_per_time,'place':place}
        if self.data['place'][str(place)] != "NULL":
            self.data['place'][str(place)] == "NULL"
            self.remove_medicine(self.data['place'][str(place)])
        self.data['medicine'].append(new_medicine)
        self.set_medicineSchedule(user,medicine_name,num_times,time_interval)
        self.set_medicineStatus(user,medicine_name,num_times)
        self.data['place'][str(place)] = medicine_name
        self.data['last_update']['info'] = "Add a new medicine"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()
        return


    def set_medicineSchedule(self,user,medicine,num_times,time_interval=None):
        # num_times : how many times the user need to take this medicine
        # format of time interval : 13,14 (13:00 to 14:00)
        for schedule in self.data["Schedules"]:
            if schedule['medicine'] == medicine and schedule['user'] == user:
                self.data["Schedules"].remove(schedule)
                self.overwrite()
        new_schedule = {'medicine':medicine,'user':user,'num_times':num_times}
        if num_times == 1:
            new_schedule['day'] = time_interval
        elif num_times == 2:
            new_schedule['morning'] = "6,8"
            new_schedule['night'] = "20,22"
        else:
            new_schedule['morning'] = "6,8"
            new_schedule['afternoon'] = "12,14"
            new_schedule['night'] = "20,22"
        self.data['Schedules'].append(new_schedule)
        self.data['last_update']['info'] = "Add a new schedule"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()
        return 


    def get_medicineSchedule(self):
        return json.dumps({'schedule':self.data['Schedules']})


    def set_medicineStatus(self,user,medicine,num_times):
        # e.g. , { Marco : { medicine1 : { morning : False, night : False }}
        # If Marco takes the medicine, the status of corresponding time will be True
        if num_times == 1:
            new_status = {'day':False}
        elif num_times == 2:
            new_status = {'morning':False,'night':False}
        elif num_times == 3:
            new_status = {'morning':False,'afternoon':False,'night':False}
        if user in self.data['Status']:
            if medicine in self.data['Status'][user]:
                self.data['Status'][user].pop(medicine)
                self.data['Status'][user][medicine] = new_status
            else:
                self.data['Status'][user][medicine] = new_status
        else:
            self.data['Status'][user] = {medicine:new_status}
        self.data['last_update']['info'] = "Add/update a status"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()
        return 


    def reset_medicineStatus(self):
        # reset status of all medicines to False (e.g. 2018/07/26 -> 2018/07/27)
        for user in self.data['Status']:
            for medicine in self.data['Status'][user]:
                if 'day' in self.data['Status'][user][medicine]:
                    self.data['Status'][user][medicine]['day'] = False
                elif 'afternoon' in self.data['Status'][user][medicine]:
                    self.data['Status'][user][medicine]['morning'] = False
                    self.data['Status'][user][medicine]['afternoon'] = False
                    self.data['Status'][user][medicine]['night'] = False
                else:
                    self.data['Status'][user][medicine]['morning'] = False
                    self.data['Status'][user][medicine]['night'] = False
        self.data['last_update']['info'] = "Add/update all status"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()
        return


    def set_medicineStatus_button(self,user,medicine,time_interval):
        # change the medicine status to True after pressing button
        # time_interval : 'day','morning','afternoon','night'
        self.data['Status'][user][medicine][time_interval] = True
        self.data['last_update']['info'] = "Add/update a status"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()
        return


    def get_medicineStatus(self):
        return json.dumps({'status':self.data['Status']})


    def set_currentUser(self,user):
        self.data['current_user']['user'] = user
        self.data['last_update']['info'] = "update the current user"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()
        return


    def get_currentUser(self):
        return json.dumps({'current_user':self.data['current_user']})


    def get_medicine(self,name=None) :
        # find the medicine based on name
        if name == None :
            return json.dumps({"medicine":self.data['medicine']})
        for e in self.data['medicine'] :
            if e['name'] == name :
                return json.dumps({"medicine":e})


    def get_placeByMedicineName(self,name):
        ''' return the place of the medicine in the box : search by medicine name'''
        for medicine in self.data['medicine']:
            if medicine['name'] == name:
                return json.dumps({'place':int(medicine['place'])})


    def get_medicineByplace(self,place) :
        # find the medicine based on place
        name = self.data['place'][str(place)]
        for e in self.data['medicine'] :
            if e['name'] == name :
                return json.dumps({"medicine":e})


    def buy_new_medicine(self,medicine_name,replace) :
        # reset the current quantity of this medicine
        for e in self.data['medicine'] :
            if e['name'] == medicine_name :
                if replace :
                    e['current_quantity'] = str(int(e['initial_quantity']))
                else:
                    e['current_quantity'] = str(int(e['current_quantity'])+int(e['initial_quantity']))
                self.data['last_update']['info'] = "Buy new medicine"
                self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
                self.overwrite()
                return


    def remove_medicine(self,name) :
        remove = True
        for e in self.data['medicine'] :
            if e['name'] == name :
                self.data['place'][str(e['place'])] = 'NULL'
                self.data['medicine'].remove(e)
        while remove:
            remove = False
            for j in self.data['Schedules']:
                if j['medicine'] == name:
                    self.data['Schedules'].remove(j)
                    remove = True
        for user in self.data['Status']:
            if name in self.data['Status'][user]:
                self.data['Status'][user].pop(name)
        self.data['last_update']['info'] = "remove medicine"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()
        return



  #############  functions about the control strategies (microservices) #############



    def set_timeInterval(self,start,end) :
        self.data['interval']['start'] = start
        self.data['interval']['end'] = end
        self.data['last_update']['info'] = "Set time interval"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def get_timeInterval(self) :
        return json.dumps({"start":self.data['interval']['start'],"end":self.data['interval']['end']})


    def set_quantity(self,medicine,current_quantity):
        for e in self.data['medicine'] :
            if e['name'] == medicine:
                e['current_quantity'] = int(current_quantity)
        self.data['last_update']['info'] = "Update quantity information"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()

    def get_quantity(self,name=None) :
        if name == None :
            # return the quantity of all medicines
            qty = {}
            for e in self.data['medicine'] :
                qty[e['name']] = e['current_quantity']
            return json.dumps({"qty":qty})
        else :
            for e in self.data['medicine'] :
                if e['name'] == name :
                    return json.dumps({"qty":{e['name']:e['current_quantity']}})
            return "No medicine"


    def get_pillsPerTime(self,name=None) :
        if name == None :
            # return pills_per_day of all medicines
            pill = {}
            for e in self.data['medicine'] :
                pill[e['name']] = e['pills_per_time']
            return json.dumps({"pill":pill})
        else :
            for e in self.data['medicine'] :
                if e['name'] == name :
                    return json.dumps({"pill":{e['name']:e['pills_per_time']}})
            return "No medicine"


    def get_temp_th(self,name=None) :
        if name == None :
            # return the temperature threshold of all medicines
            tempth = {}
            for e in self.data['medicine'] :
                tempth[e['name']] = e['temperature_threshold']
            return json.dumps({"tempth":tempth})
        else :
            for e in self.data['medicine'] :
                if e['name'] == name :
                    return json.dumps({"tempth":{e['name']:e['temperature_threshold']}})
            return "No medicine"


    def get_humi_th(self,name=None) :
        if name == None :
            # return the humidity threshold of all medicines
            humith = {}
            for e in self.data['medicine'] :
                humith[e['name']] = e['humidity_threshold']
            return json.dumps({"humith":humith})
        else :
            for e in self.data['medicine'] :
                if e['name'] == name :
                    return json.dumps({"humith":{e['name']:e['humidity_threshold']}})
            return "No medicine"



  ############  mqtt-topic about the microservices and Thingspeak adaptor ############



    def set_topic_pressing_control(self,sub,pub):
        self.data['pressing_control']['subscriber_topic'] = sub
        self.data['pressing_control']['publisher_topic'] = pub
        self.data['last_update']['info'] = "Set topic-pressing control"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def set_topic_time_shift(self,pub):
        self.data['time_shift']['publisher_topic'] = pub
        self.data['last_update']['info'] = "Set topic-time shift"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def set_topic_quantity_control(self,sub_button,sub_timeShift,pub):
        self.data['quantity_control']['subscriber_button_topic'] = sub_button
        self.data['quantity_control']['subscriber_timeShift_topic'] = sub_timeShift
        self.data['quantity_control']['publisher_topic'] = pub
        self.data['last_update']['info'] = "Set topic-quantity control"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def set_topic_env_control(self,sub,pub):
        self.data['environment_control']['subscriber_topic'] = sub
        self.data['environment_control']['publisher_topic'] = pub
        self.data['last_update']['info'] = "Set topic-environment control"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def set_thingspeak_adaptor(self,channelID,api_key) :
        self.data['Thingspeak_adaptor']['channelID'] = channelID
        self.data['Thingspeak_adaptor']['api_key'] = api_key
        self.data['Thingspeak_adaptor']['sublisher_topic'] = "channels/"+channelID+"/publish/"+api_key
        self.data['last_update']['info'] = "Set topic-Thingspeak_adaptor control"
        self.data['last_update']['time'] = strftime("%Y-%m-%d %H:%M", gmtime())
        self.overwrite()


    def get_topic_pressing_control(self):
        return json.dumps({"sub":self.data['pressing_control']['subscriber_topic'],
                           "pub":self.data['pressing_control']['publisher_topic']})


    def get_topic_time_shift(self):
        return json.dumps({"pub":self.data['time_shift']['publisher_topic']})


    def get_topic_quantity_control(self):
        return json.dumps({"sub_button":self.data['quantity_control']['subscriber_button_topic'],
                           "sub_timeShift":self.data['quantity_control']['subscriber_timeShift_topic'],
                           "pub":self.data['quantity_control']['publisher_topic']})


    def get_topic_env_control(self):
        return json.dumps({"sub":self.data['environment_control']['subscriber_topic'],
                           "pub":self.data['environment_control']['publisher_topic']})


    def get_topic_thingspeak_adaptor(self) :
        return json.dumps({"sub":self.data['Thingspeak_adaptor']['subscriber_topic']})
















