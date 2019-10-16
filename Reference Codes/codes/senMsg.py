import json
from datetime import datetime
class senMsg(object):
	'''
	class to define the structure of sensor readings
	'''
	
	def __init__(self,bn='',bt = datetime(2000,1,1)):
		self.bn = bn
		self.bt = bt
		self.e = []
	def addSensor(self,name,unit,value):
		tempDict = {'n':name,
		'u':unit,
		'v':value
		}
		self.e.append(tempDict)
	def toDict(self):
		tempDict = {
		'bn':self.bn,
		'bt':self.bt,
		'e':self.e
		}
		return tempDict
	def toJson(self):
		tempJson = self.toDict()
		# Convert datetime object to UNIX timestamp
		# Json doesnt support object type datetime
		tempJson['bt'] = int(tempJson['bt'].strftime('%s'))
		response = json.dumps(tempJson)
		return response
	def iaq_values(self):
		temp = None
		humid = None
		co2 = None
		voc = None

		for sensor in self.e:
			if 'temp' in sensor['n']:
				temp = sensor['v']
			elif 'humid' in sensor['n']:
				humid = sensor['v']
			elif 'co2' in sensor['n'] :
				co2 = sensor['v']
			elif 'voc' in sensor['n']:
				voc = sensor['v']
		temp_dict = {'temp':temp,'humid':humid,
				     'co2':co2,'voc':voc}
		return temp_dict

	def fromJson(self,jsonfile):
		self.bn = jsonfile['bn']
		# Convert UNIX timestamp back to datetime object
		self.bt = datetime.fromtimestamp(jsonfile['bt'])
		self.e = jsonfile['e']
