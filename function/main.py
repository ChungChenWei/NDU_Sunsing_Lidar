# main 
# version : 

# new		: 
# structure : 
# target	: 
# 1. 
from datetime import datetime as dtm
from datetime import timedelta as dtmdt
from os.path import join as pth
from lidar.dt_handle import * 

def run():
	

	# start_dtm = dtm(2020,11,20,0,0,0)
	# final_dtm = dtm(2020,11,21,0,0,0)
	# path = pth('..','data','Lidar_Sunsing_NDU_testdata')
	# reader = NDU.reader(path,start_dtm,final_dtm,reset=False)
	# dt = reader.get_data()







if __name__=='__main__':
	print(f'\nprogram : {__file__}')
	print('version : \n')
	start = dtm.now().timestamp()
	print(f"program start : {dtm.now().strftime('%m/%d %X')}\n")


	run()


	final = dtm.now().timestamp()
	runtime = (final-start)/60.
	print(f'\nProgram done\nrunning time = {int(runtime):3d} min {(runtime-int(runtime))*60.:6.3f} s')


