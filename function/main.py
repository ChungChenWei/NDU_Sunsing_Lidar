# main 
# version : 

# new	  	: 
# structure : 
# target  	: 
# 1. 
if __name__=='__main__':
	import sys
	print(f'\nprogram : {sys.argv[0]}')
	print('version : \n')

	from datetime import datetime as dtm
	start = dtm.now().timestamp()
	print(f"program start : {dtm.now().strftime('%m/%d %X')}\n")

# from datetime import datetime as dtm
# from datetime import timedelta as dtmdt
from os.path import join as pth
# import numpy as n

# from func_dt_handle import * 
# from func_plot import *

from lidar.dt_handle import *
from lidar.plot import plot





start_dtm = dtm(2020,11,20,0,0,0)
final_dtm = dtm(2020,11,21,0,0,0)
path = pth('..','data','Lidar_Sunsing_NDU_testdata')

reader = NDU.reader(path,start_dtm,final_dtm,reset=False)
dt = reader.get_data(mean_freq='10T')



# start_dtm = dtm(2015,1,23,12,30,0)
# final_dtm = dtm(2015,1,23,15,30,0)
# path = pth('..','data','Lidar_Sunsing_SSC_testdata')
# reader = SSC.reader(path,start_dtm,final_dtm,reset=False)
# dt1 = reader.get_data()


# start_dtm = dtm(2020,11,27,0,0,0)
# final_dtm = dtm(2020,11,28,0,0,0)
# path = pth('..','data','Lidar_Sunsing_RCEC_testdata')
# reader = RCEC.reader(path,start_dtm,final_dtm,reset=False)
# dt2 = reader.get_data()

plot.plot_all(dt,fig_path=pth('..','picture'))

# start_dtm = dtm(2014,12,29,1,30,0)
# final_dtm = dtm(2014,12,29,2,0,0)
# path = pth('..','data','Lidar_Sunsing_TORI_testdata')
# reader = TORI.reader(path,start_dtm,final_dtm,reset=False)
# dt3 = reader.get_data()
















#=============================================================================
if __name__ == '__main__':
	final = dtm.now().timestamp()
	runtime = (final-start)/60.
	print(f'\nProgram done\nrunning time = {int(runtime):3d} min {(runtime-int(runtime))*60.:6.3f} s')