#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 19:50:12 2018

@author: pi
"""

import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                            0x8915,
                            struct.pack('256s',bytes(ifname[:15],'utf-8'))
                         )[20:24])

print(get_ip_address('eth0'))

ip = get_ip_address('eth0')