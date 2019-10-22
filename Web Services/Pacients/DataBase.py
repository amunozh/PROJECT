import json
import time
import paho.mqtt.client as mqtt
import requests
import os
cwd = os.getcwd()

class Llamado(object):
    def __init__(self):
        self.rxmsg="No Message"
    def sub(self,topic,broker):
        client = mqtt.Client("Prueba")
        client.on_message = self.on_message
        client.connect(broker,port=1883)  # connect to broker
        client.loop_start()
        client.subscribe(topic)
        time.sleep(10)
        #print(self.rxmsg)
        if self.rxmsg == '0':
            client.disconnect()
            msg ='No MQTT'
            return (str(msg))
        else:
            client.disconnect()
            msg=str(self.rxmsg)
            self.rxmsg='0'
            return msg

    def on_message(self, client, userdata, message):
        print("message received " ,str(message.payload.decode("utf-8")))
        self.rxmsg=str(message.payload.decode("utf-8"))
        client.disconect()
        return

class Patients(object):
    def __init__(self, IPs):
        self.IPs = IPs
        res = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/show_patients")
        re = res.content.decode('utf-8')
        jre = json.loads(re)
        print(jre)
        self.Pacientlist=jre
        res = requests.get("http://" + '192.168.1.204' + ":" + '8383' + "/database/all_patients")
        re = res.content.decode('utf-8')
        jre = json.loads(re)
        print(jre)
        self.Datalist=jre


    def read_list(self):
        for pac in self.Pacientlist:
            HDev = pac['health_device']
            print(HDev)
            js = json.dumps({'ID': HDev})
            response = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/search_device?json_msg=" + js)
            r = response.content.decode('utf-8')
            jr = json.loads(r)
            top=str(jr['end_point'][0])
            H=Llamado()
            HR=H.sub(top, self.IPs.IPBroker)
            print("HR Leido")

            LocDev=pac['location_device']
            js=json.dumps({'ID': LocDev})
            response = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/search_device?json_msg=" + js)
            r = response.content.decode('utf-8')
            jr = json.loads(r)
            print("Location")
            print(jr)
            top=str(jr['end_point'][0])
            Loc = H.sub(top, self.IPs.IPBroker)
            U=json.loads(Loc)
            L=U['e'][0]['v']
            print(L)

            Update=self.update_measurements(pac['ID'],HR,L)
            print("Actualizacion")
            print(Update)

    def update_measurements(self, ID, HR, Loc):
        j='0'
        Pcts = self.Datalist
        for pat in Pcts:
            if pat['ID']==ID:
                    j = {"Heart Rate": HR, "Location": Loc, "timestamp": time.time()}
                    if len(Pcts[ID]["data"])<=10:
                        Pcts[ID]["data"].append(j)
                    else:
                        Pcts[ID]["data"].pop([-1])
                        Pcts[ID]["data"].append(j)
                    return "last update" + str(j)
        if j=='0':
            j = {"ID": ID, "data": [{"Heart Rate": HR, "Location": Loc, "timestamp": time.time()}]}
            Pcts.append(j)

        return "last update"+ str(j)


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
    PortAddr="8585"
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
    #while (True):
    c.read_list()
    print("Post")
    js = json.dumps(c.Datalist)
    response = requests.post("http://" + "192.168.1.204" + ":" + "8383" + "/database/update_DB?json_msg=" + js)
    r = response.content.decode('utf-8')
    print(r)
