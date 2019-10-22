import json
import time
import paho.mqtt.client as mqtt
import requests
import os
cwd = os.getcwd()

class Llamado(object):
    def __init__(self):
        pass
    def sub(self,topic,broker):
        client = mqtt.Client()
        client.on_message = self.on_message
        client.connect(broker)  # connect to broker
        client.loop_start()
        client.subscribe(topic)
        msg=client.on_message.message.payload.decode("utf-8")
        time.sleep(30)
        print(msg)
        if msg == None:
            client.loop_stop()
            msg='0'
            return (str(msg))
        else:
            client.loop_stop()
            return(str(msg))

    def on_message(self, client, userdata, message):
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)

class Patients(object):
    def __init__(self,IPs):
        res = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/show_patients")
        re = res.content.decode('utf-8')
        jre = json.loads(re)
        print(jre)
        self.Pacientlist=jre
        res = requests.get("http://" + self.IPs.IPCat + ":" + 8383 + "/database/all_patients")
        re = res.content.decode('utf-8')
        jre = json.loads(re)
        print(jre)
        self.Datalist=jre
        self.IPs=IPs

    def read_list(self):
        for pac in self.Pacientlist:
            HDev = pac['health_device']
            js = json.dumps({'ID': HDev})
            response = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/search_device?json_msg=" + js)
            r = response.content.decode('utf-8')
            jr = json.loads(r)
            HR=Llamado.sub(jr['end_point'][0],self.IPs.IPBroker)
            print(HR)
            LocDev=pac['Location Device']
            js=json.dumps({'ID': LocDev})
            response = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/search_device?json_msg=" + js)
            r = response.content.decode('utf-8')
            jr = json.loads(r)
            Loc = Llamado.sub(jr['end_point'][0], self.IPs.IPBroker)
            print(Loc)
            # Update=self.update_measurements(pac['ID'],HR,Loc)

    def update_measurements(self, ID, HR, Loc):

        Pcts = self.Datalist['Pacients']

        if Pcts[ID] in Pcts:
                j = {"Heart Rate": HR, "Location": Loc, "timestamp": time.time()}
                if len(Pcts[ID]["data"])<=10:
                    Pcts[ID]["data"].append(j)
                else:
                    Pcts[ID]["data"].pop([-1])
                    Pcts[ID]["data"].append(j)
        else:
            j={"ID":ID,"data":[{"Heart Rate":HR,"Location":Loc,"timestamp":time.time()}]}
            Pcts.append(j)
        return "last update"+ j


class IPS(object):
    def __init__(self, IPAdd,PAdd,IPCat,PCat,IPBroker,PBroker,):
        self.IPAdd=IPAdd
        self.IPCat=IPCat
        self.IPBroker=IPBroker
        self.PAdd=PAdd
        self.PCat=PCat
        self.PBroker=PBroker

if __name__ == '__main__':
    IPAddr="192.168.1.122"
    PortAddr="8181"
    #Contact to Address Manager to get the Catalog IP and Port
    response = requests.get("http://"+IPAddr+":"+PortAddr + "/address_manager/get")
    r=response.content.decode('utf-8')
    jr=json.loads(r)
    print(jr)
    IPCat=jr['ip']
    PortCat=str(jr['port'])

    # Contact to Catalog to get the Broker IP and Port
    response = requests.get("http://" + IPCat + ":"+PortCat + "/catalog/broker")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)
    IPBroker = jr['ip']
    PortBroker = jr['port']

    #Save all IPs and Ports in a Variable
    Dir = IPS(IPAddr, PortAddr, IPCat, PortCat, IPBroker, PortBroker)

    #
    c = Patients(Dir)
    while (True):
        c.read_list()
