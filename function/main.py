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
# from os.path import join as pth
# import numpy as n

from func_dt_handle import * 
from func_plot import *





















#=============================================================================
if __name__ == '__main__':
	final = dtm.now().timestamp()
	runtime = (final-start)/60.
	print(f'\nProgram done\nrunning time = {int(runtime):3d} min {(runtime-int(runtime))*60.:6.3f} s')