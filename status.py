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
data['disks'] = diskuse()
if 'apis' in config:
	for kk in config['apis'].keys():
		k = str(kk)
		data[k] = getremotejson(config['apis'][k])

publish(config['host'], config['topic'], data)

