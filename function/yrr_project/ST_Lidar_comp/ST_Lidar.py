# main 
# version : 

# new		: 
# structure : 
# target	: 
# 1. 
import sys
from os.path import join as pth
sys.path.insert(1,pth('..','..'))

from datetime import datetime as dtm
from datetime import timedelta as dtmdt

from lidar.dt_handle import *

import numpy as n
from lidar.plot import plot
# from ground import *




"""


"""


## time decorater
def __timer(func):
	def __wrap():
		print(f'\nPROGRAM : {__file__}\n')
		__st = dtm.now().timestamp()

		## main function
		_out = func()

		__fn = dtm.now().timestamp()
		__run = (__fn-__st)/60.

		print(f'\nProgram done\nrunning time = {int(__run):3d} min {(__run-int(__run))*60.:6.3f} s')
		return _out

	return __wrap





## (1) linear interpolate lidar data
'''
start_dtm = dtm(2021,4,1,0,0,0)
final_dtm = dtm(2021,4,6,0,0,0)
path = pth('..','..','..','data','Lidar_NDU','use')
reader = NDU.reader(path,start_dtm,final_dtm)
dt = reader.get_data()


dt_u, dt_v = -n.sin(dt['wd']/180.*n.pi)*dt['ws'], -n.cos(dt['wd']/180.*n.pi)*dt['ws']


def height_inter(_df,inter_h):

	key_lst = list(_df.keys())
	inter_lst = n.arange(key_lst[0],key_lst[-1]+inter_h,inter_h).tolist()

	add_lst = inter_lst.copy()
	[ add_lst.remove(_) for _ in key_lst ]

	for _ in add_lst: _df[_] = n.nan

	return _df[inter_lst].interpolate(axis=1)

def uv2wswd(u,v):
	return n.sqrt((u**2)+(v**2)), (n.arctan2(-u,-v)*180./n.pi)%360.

ws_inte, wd_inte = uv2wswd(height_inter(dt_u,50),height_inter(dt_v,50))

## plot 
plot.plot_all({'nam':'inteNDU','ws':ws_inte,'wd':wd_inte,'z_ws':dt['z_ws']},pth('picture'),tick_freq='24h')

# '''


## (2) get ST at wanted time, plot height-time






## (3) 

















