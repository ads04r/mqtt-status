#!/usr/bin/python3

import paho.mqtt.client as mqtt
import json, os, sys, urllib

def publish(host, topic, data):

	broker = mqtt.Client('status')
	broker.connect(host)
	broker.publish(topic, json.dumps(data))
	broker.disconnect()

def getremotejson(url):
	operUrl = urllib.request.urlopen(url)
	if(operUrl.getcode()==200):
		data = json.loads(operUrl.read())
	else:
		data = {}
	return data

#               0    Under-voltage detected
#               1    Arm frequency capped
#               2    Currently throttled
#               3    Soft temperature limit active
#              16    Under-voltage has occurred
#              17    Arm frequency capping has occurred
#              18    Throttling has occurred
#              19    Soft temperature limit has occurred

def power():

	cmd = "vcgencmd get_throttled | sed 's/^throttled=//'"
	with os.popen(cmd) as sp:
		data = int(sp.read().strip(), 0)
	ret = []
	for i in range(0, 19):
		ovr = pow(2, (18 - i))
		if data>=ovr:
			data = data - ovr
			ret.append(True)
		else:
			ret.append(False)
	return ret

def temperature():

	cmd = "vcgencmd measure_temp | sed 's/^temp=//' | sed \"s/'/|/\""
	with os.popen(cmd) as sp:
		data = sp.read().strip().split("|")
	ret = {'value': float(data[0]), 'unit': data[1]}
	return ret

def diskuse():

	cmd = "df | sed 's/  */|/g'"
	headers = []
	data = []
	with os.popen(cmd) as sp:
		for l in sp.read().split('\n'):
			ll = l.split('|')
			if len(headers) == 0:
				headers = ll
				continue
			item = {}
			for i in range(0, len(ll)):
				item[headers[i]] = ll[i]
			if len(item) > 1:
				data.append(item)

	ret = []
	for item in data:
		if not ('Mounted' in item):
			continue
		if not ('Used' in item):
			continue
		if not ('Available' in item):
			continue
		ret.append([item['Mounted'], int(item['Available']), int(item['Used'])])

	return ret

base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
config_file = os.path.join(base_path, 'config.json')

with open(config_file) as fp:
	config = json.load(fp)

data = {}
data['temperature'] = temperature()
data['power'] = power()
data['disks'] = diskuse()
if 'apis' in config:
	for kk in config['apis'].keys():
		k = str(kk)
		data[k] = getremotejson(config['apis'][k])

publish(config['host'], config['topic'], data)

