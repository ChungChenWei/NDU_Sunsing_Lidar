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
# from lidar.dt_handle import *
# from lidar.plot import plot
from ground import *



def run():

	
	# from func_plot import *

	
	## NDU
	# start_dtm = dtm(2020,11,20,0,0,0)
	# final_dtm = dtm(2020,11,21,0,0,0)
	# path = pth('..','data','test','Lidar_Sunsing_NDU_testdata')
	# reader = NDU.reader(path,start_dtm,final_dtm,reset=False)
	# dt = reader.get_data(mean_freq='10T')

	# plot.plot_all(dt,pth('..','picture'))

	## SSC
	# start_dtm = dtm(2021,4,1,14,30,0)
	# final_dtm = dtm(2021,4,3)
	# path = pth('..','data','Lidar_SSC')
	# reader = SSC.reader(path,start_dtm,final_dtm,reset=False)
	# dt = reader.get_data()

	# plot.plot_all(dt,pth('..','picture'))


	## RCEC
	# start_dtm = dtm(2021,4,1)
	# final_dtm = dtm(2021,4,3)
	# path = pth('..','data','Lidar_RCEC')
	# reader = RCEC.reader(path,start_dtm,final_dtm,reset=False)
	# dt = reader.get_data(dtm(2021,4,1,18),dtm(2021,4,2,18))

	# plot.plot_all(dt,pth('..','picture'),freq='1h')

	## GRIMM
	# start_dtm = dtm(2021,4,1)
	# final_dtm = dtm(2021,4,3)
	# path = pth('..','data','GRIMM')
	# reader = GRIMM.reader(path,start_dtm,final_dtm,reset=True)
	# dt = reader.get_data()


	## WXT
	start_dtm = dtm(2021,4,1)
	final_dtm = dtm(2021,4,4)
	path = pth('..','data','WXT')
	wxt = WXT.reader(path,start_dtm,final_dtm,reset=False)
	# dt = wxt.get_data()

	dt = wxt.plot(pth('..','picture'),tick_freq='12h',mean_freq='1h')

	return dt




if __name__=='__main__':
	print(f'\nprogram : {sys.argv[0]}')
	print('version : \n')
	start = dtm.now().timestamp()
	print(f"program start : {dtm.now().strftime('%m/%d %X')}\n")


	dt = run()


	final = dtm.now().timestamp()
	runtime = (final-start)/60.
	print(f'\nProgram done\nrunning time = {int(runtime):3d} min {(runtime-int(runtime))*60.:6.3f} s')


