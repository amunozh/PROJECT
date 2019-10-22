# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 12:18:37 2017

@author: Andres Hernando
"""
import json
import time
import cherrypy
import threading
import base64



'''
Exception codes:
- 404 : Don't find the requested resource
- 204 : The requested resource is empty
'''
class catalog:
    def __init__(self, filename):
        self.filename = filename
        file = open(self.filename, 'r')  # open the file for reading it
        self.catalog = json.load(file)  # read the file and convert to json
        file.close()

    def broker(self):
        broker = self.catalog['brokers']

        if broker:
            return (broker)  # return the brokers of the catalog.json
        else:
            return ({"brokers": None})

    def search_device(self, ID):
        devices = self.catalog['devices']  # Select the devices JSON list

        if devices:
            for dev in devices:  # Search the device
                if dev['ID'] == ID: #when find it return it
                    return dev

            return(404)
        else:
            return(204)

    def search_service(self, ID):
        services = self.catalog['services']  # Select the devices JSON list

        if services:
            for serv in services:  # Search the device
                if serv['ID'] == ID:  # when find it return it
                    return serv

            return (404)  # if dont find it show error
        else:
            return (204)

    def search_user(self, ID):
        users = self.catalog['users']  # Select the devices JSON list

        if users:
            for user in users:  # Search the device
                if user['ID'] == ID:
                    return user

            return (404)  # if dont find it show error
        else:
            return (204)


    def add_device(self, ID, end_point, resources):

        devices = self.catalog['devices']

        for dev in devices:
            if dev['ID'] == ID:
                return(False)

        new_dev = {
            'ID': ID,
            'end_point': end_point,
            'resources': resources,
            'timestamp': time.time()}

        self.catalog['devices'].append(new_dev)

        #update the file
        file = open(self.filename, 'r+')
        file.seek(0)
        print(self.catalog)
        file.write(json.dumps(self.catalog))
        file.truncate()
        file.close()
        return new_dev

    def add_service(self, ID, end_point, resources):

        services = self.catalog['services']

        for serv in services:
            if serv['ID'] == ID:
                return(False)

        new_serv = {
            'ID': ID,
            'end_point': end_point,
            'resources': resources,
            'timestamp': time.time()}

        self.catalog['services'].append(new_serv)

        #update the file
        file = open(self.filename, 'r+')
        file.seek(0)
        print(self.catalog)
        file.write(json.dumps(self.catalog))
        file.truncate()
        file.close()
        return new_serv

    def add_user(self, name, surname , ID_telegram):
        users = self.catalog['users']

        if users:
            for user in users:
                if user['ID'] == ID_telegram:
                    return(False)

        new_user = {
            'ID': ID_telegram,
            'name': name,
            'surname': surname,
            'patients': []}

        self.catalog['users'].append(new_user)

        #update the file
        file = open(self.filename, 'r+')
        file.seek(0)
        print(self.catalog)
        file.write(json.dumps(self.catalog))
        file.truncate()
        file.close()
        return new_user


    def add_patient(self, ID, name, surname , health_device, location_device, room_ID):
        patients = self.catalog['patients']

        for patient in patients:
            if patient['ID'] == ID:
                return(False)

        new_patient = {
            'ID': ID,
            'name': name,
            'surname': surname,
            'caretaker': None,
            'health_device': health_device,
            'location_device': location_device,
            'room_ID': room_ID}

        self.catalog['patients'].append(new_patient)

        #update the file
        file = open(self.filename, 'r+')
        file.seek(0)
        print(self.catalog)
        file.write(json.dumps(self.catalog))
        file.truncate()
        file.close()
        return new_patient

    def caretaker(self, patient_ID, caretaker_ID):
        patients = self.catalog['patients']  # Select the devices JSON list

        if patients:
            for patient in patients:  # Search the device
                if patient['ID'] == patient_ID:
                    patient['caretaker'] = caretaker_ID
                    return (patient)

            return (404)  # if dont find it show error
        else:
            return (204)

        #update file
    def devices(self):
        return (self.catalog['devices'])

    def users(self):
        return (self.catalog['users'])

    def services(self):
        return (self.catalog['services'])

    def patients(self):
        return (self.catalog['patients'])

    def refresh(self, ID):
        devices = self.catalog['devices']
        ID = 0
        print(ID)
        if devices:
            for dev in devices:  # Search the device
                if dev['ID'] == ID:
                    dev['timestamp'] = time.time()

            file = open(self.filename, 'r+')
            file.seek(0)
            file.write(json.dumps(self.catalog))
            file.truncate()
            file.close()

            return (dev)
        else:
            return ({"message": "device not found"})

    def update(self):

        delay=300 #5 minutes
        print("updating")
        devices = self.catalog['devices']
        indexes = []
        if devices:
            for dev in devices:
                silence = time.time()-float(dev['timestamp'])
                if silence >= delay:
                    index = devices.index(dev)

        if indexes:
            for index in indexes:
                print("deleting device %s" % (dev['ID']))
                del devices[index]



        file = open(self.filename, 'r+')
        file.seek(0)
        file.write(json.dumps(self.catalog))
        file.truncate()
        file.close()





