#coding utf-8

import labrad 
import numpy as np
import time
from datetime import datetime as dt


cxn = labrad.connection('172.27.61.12')
pv = cxn.parametervault
try:
    while True:
        hr = dt.now().hour
        min = dt.now().minute
        sec = dt.now().second
        pv.set_parameter('test','test',(hr,min,sec))
        print 'wrote on parameterVault',hr,min,sec
        time.sleep(3)
finally:
        hr = dt.now().hour
        min = dt.now().minute
        sec = dt.now().second
        pv.save_parameters_to_registry()