# main 
# version : 

# new		: 
# structure : 
# target	: 
# 1. 
import sys
sys.path.insert(1,pth('..','..')

from datetime import datetime as dtm
from datetime import timedelta as dtmdt
from os.path import join as pth
from lidar.dt_handle import *
# from lidar.plot import plot
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

























# def wind_ave(ws,wd,ave_freq):

	# _u, _v = -n.sin(_wd/180.*n.pi)*_ws, -n.cos(_wd/180.*n.pi)*_ws
	
	# def uv2wswd(u,v):
		# return n.sqrt((u**2)+(v**2)), (n.arctan2(-u,-v)*180./n.pi)%360.


	# return uv2wswd(_u.resample(ave_freq,label='right').mean(),_v.resample(ave_freq,label='right').mean())
