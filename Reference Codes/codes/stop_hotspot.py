#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 20:25:01 2018

@author: pi
"""

import os
import subprocess

output = str(subprocess.check_output(["create_ap --list"],shell=True))
output_list = output.split("\\n")[2].split(" ")

os.system("sudo create_ap --stop "+output_list[1])
os.system("sudo create_ap --stop "+output_list[0])






