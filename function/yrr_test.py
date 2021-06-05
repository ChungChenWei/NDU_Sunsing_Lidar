# main 
# version : 

# new		: 
# structure : 
# target	: 
# 1. 
import sys
from datetime import datetime as dtm
from datetime import timedelta as dtmdt
from os.path import join as pth
from lidar.dt_handle import *
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


@__timer
def run():


	res = 0
	fig_pth = pth('..','picture')

	## NDU
	# '''
	start_dtm = dtm(2021,4,1,0,0,0)
	final_dtm = dtm(2021,4,6,0,0,0)
	path = pth('..','data','Lidar_NDU','use')
	reader = NDU.reader(path,start_dtm,final_dtm,reset=res)
	# dt = reader.get_data(dtm(2021,4,2,0,0,0),dtm(2021,4,5,0,0,0))
	dt = reader.get_data()

	plot.plot_all(dt,fig_pth,tick_freq='24h')
	# '''

	## SSC
	# '''
	start_dtm = dtm(2021,4,1)
	final_dtm = dtm(2021,4,6)
	path = pth('..','data','Lidar_SSC')
	reader = SSC.reader(path,start_dtm,final_dtm,reset=res)
	# dt = reader.get_data(dtm(2021,4,2,0,0,0),dtm(2021,4,5,0,0,0))
	dt = reader.get_data()

	plot.plot_all(dt,fig_pth,tick_freq='24h')
	# '''

	## RCEC
	# '''
	start_dtm = dtm(2021,4,1)
	final_dtm = dtm(2021,4,6)
	path = pth('..','data','Lidar_RCEC')
	reader = RCEC.reader(path,start_dtm,final_dtm,reset=res)
	# dt = reader.get_data(dtm(2021,4,2,0,0,0),dtm(2021,4,5,0,0,0))
	dt = reader.get_data()

	plot.plot_all(dt,fig_pth,tick_freq='24h')
	# '''

	## TORI
	# '''
	start_dtm = dtm(2021,4,1)
	final_dtm = dtm(2021,4,6)
	path = pth('..','data','Lidar_TORI')
	reader = TORI.reader(path,start_dtm,final_dtm,reset=res)
	# dt = reader.get_data(dtm(2021,4,2,0,0,0),dtm(2021,4,5,0,0,0))
	dt = reader.get_data()

	plot.plot_all(dt,fig_pth,tick_freq='24h')
	# '''

	## GRIMM
	'''
	start_dtm = dtm(2021,4,1)
	final_dtm = dtm(2021,4,4)
	path = pth('..','data','GRIMM')
	grimm = GRIMM.reader(path,start_dtm,final_dtm,reset=False)
	# dt = grimm.get_data()
	# dt = grimm.plot(pth('..','picture'),dtm(2021,4,2,6),dtm(2021,4,2,18),tick_freq='2h',mean_freq='6T')
	dt = grimm.plot(pth('..','picture'),start_dtm,final_dtm,tick_freq='12h',mean_freq='30T')
	
	# '''

	## WXT
	'''
	start_dtm = dtm(2021,4,1)
	final_dtm = dtm(2021,4,5)
	path = pth('..','data','WXT')
	wxt = WXT.reader(path,start_dtm,final_dtm,reset=False)
	dt = wxt.get_data()

	dt = wxt.plot(pth('..','picture'),dtm(2021,4,3,12),dtm(2021,4,4,16),tick_freq='6h',mean_freq='30T')
	# '''
	return dt

	
	






if __name__=='__main__':

	dt = run()

