# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 00:34:10 2019

@author: Miguel
"""

import paho.mqtt.publish as publish
import json
Cont=json.dumps({'Heart Rate':'120'})
publish.single('Miguel1096/test/HR', Cont, hostname='mqtt.eclipse.org')