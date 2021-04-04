# initial function 
# version : 

# target : 
# 1. read data and process

# import pickle as pkl
# from numpy import array, nan
# from pandas import date_range, concat, read_table



from datetime import datetime as dtm
from datetime import timedelta as dtmdt
from os import listdir, mkdir
from os.path import join as pth, exists, dirname, realpath
from pandas import read_csv
from numy import sin, cos, pi
from metpy.units import units
import metpy.calc as mcalc




# initial function 
# version : 

# target : 
# 1. read data and process

from datetime import datetime as dtm
from datetime import timedelta as dtmdt
from os import listdir, mkdir
from os.path import join as pth, exists, dirname, realpath
import pickle as pkl
from numpy import array, nan
from pandas import date_range, concat, read_table


## bugs box
"""




# """


__all__ = [
		'get_data',
		'plot',
	]







    ##input dataname : is a string
    ##output Vars is a dataframe
    data = read_csv(data_name, skiprows = (0, 2, 3), parse_dates = ['TIMESTAMP'])
    



    ##pick the data and rename
    Vars = data[['TIMESTAMP', 'airtemp_Avg', 'relhumidity_Avg', 'airpressure_Avg', 'Wsavg_Avg', 'Wdavg_Avg', 
             'WindDir_SD1_WVT']]

    ##add Td
    T = Vars['T'][:].to_numpy()
    RH = Vars['RH'][:].to_numpy()
    Td = mcalc.dewpoint_from_relative_humidity(T*units.degC, RH/100).m
    Vars['Td'] = Td
    
    ##add U, V
    ws = Vars['Ws'][:]
    wd = Vars['Wd'][:]
    U = -sin(wd/180.*pi)*ws
    V = -cos(wd/180.*pi)*ws
    Vars['U'] = U
    Vars['V'] = V





















class reader:

	## initial setting
	## input path and start time, final time
	## because the pickle file will be generated after read raw data first time, 
	## if want to reread the rawdata, please set 'reser=True'
	def __init__(self,path,start,final,reset=False):
		print(f'\nGRIMM')
		print('='*65)
		print(f"Reading file and process data")

		## class parameter
		self.index = lambda _freq: date_range(start,final,freq=_freq)
		self.path  = path
		self.reset = reset
		# self.meta  = meta_dt['lidar'][_nam]
		self.nam   = 'GRIMM'
		self.pkl_nam = f'grimm.pkl'
		self.__time  = (start,final)
		
		print(f" from {start.strftime('%Y-%m-%d %X')} to {final.strftime('%Y-%m-%d %X')}")
		print('='*65)
		print(f"{dtm.now().strftime('%m/%d %X')}")




	def __raw_reader(self,_flist,_file):
		## customize each instrument
		## read one file
		with open(pth(self.path,_file),'r',encdoe='utf-8',errors='ignore') as f:


			_rename = {'TIMESTAMP' 		 : 'time', 
					   'airtemp_Avg'	 : 'temp', 
					   'relhumidity_Avg' : 'RH', 
					   'airpressure_Avg' : 'P', 
					   'Wsavg_Avg'		 : 'ws',
					   'Wdavg_Avg'		 : 'wd',
					   'WindDir_SD1_WVT' : 'wd_std'}

			_temp = read_csv(data_name,skiprows=(0,2,3),parse_dates=['TIMESTAMP']).rename(columns=_rename).set_index('time')

			_temp['temp_dew'] = mcalc.dewpoint_from_relative_humidity(_temp['temp']*units.degC,_temp['RH']/100).m
			_temp['u'] = -sin(_temp['wd']/180.*pi)*_temp['ws']
			_temp['v'] = -cos(_temp['wd']/180.*pi)*_temp['ws']


			
			_flist.append(_temp.resample('6T').mean())



		return _flist

	# def __raw_process(self,_flist,_freq):
	def __raw_process(self,_flist):
		## customize each instrument
		# breakpoint()
		# out = concat(_flist).resample(_freq).mean().reindex(self.index(_freq))
		out = concat(_flist)
		return out



	## read raw data
	def __reader(self):

		## read pickle if pickle file exisits and 'reset=False' or process raw data
		if (self.pkl_nam in listdir(self.path))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle of {self.nam}")
			with open(pth(self.path,self.pkl_nam),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of {self.nam} and process raw data")

		##=================================================================================================================
		## metadata parameter
		# ext_nam, dt_freq, height, col_fun, col_nam, out_nam, oth_col = self.meta.values()

		## read raw data
		f_list = []
		for file in listdir(self.path):
			if '.txt' not in file.lower(): continue
			print(f"\r\t\treading {file}",end='')

			f_list = self.__raw_reader(f_list,file)
		print()

		# fout = self.__raw_process(f_list,dt_freq)
		fout = self.__raw_process(f_list)

		return fout



	## get process data
	def get_data(self,start=None,final=None,mean_freq=None):

		## get dataframe data and process to wanted time range
		# _freq = mean_freq if mean_freq is not None else self.meta['freq']
		self.__time = (start,final) if start is not None else self.__time



		return self.__reader().loc[self.__time[0]:self.__time[-1]].resample(_freq).mean()






	# def plot(self):

































def read_WXT(data_name):
    ##input dataname : is a string
    ##output Vars is a dataframe
    data = read_csv(data_name, skiprows = (0, 2, 3), parse_dates = ['TIMESTAMP'])
    
    ##pick the data and rename
    Vars = data[['TIMESTAMP', 'airtemp_Avg', 'relhumidity_Avg', 'airpressure_Avg', 'Wsavg_Avg', 'Wdavg_Avg', 
             'WindDir_SD1_WVT']]
    Vars = Vars.rename({'TIMESTAMP':'Time', 'airtemp_Avg':'T', 'relhumidity_Avg':'RH', 
             'airpressure_Avg':'P', 'Wsavg_Avg':'Ws', 'Wdavg_Avg':'Wd', 'WindDir_SD1_WVT':'Wd_std'}, axis = 1)
    ##add Td
    T = Vars['T'][:].to_numpy()
    RH = Vars['RH'][:].to_numpy()
    Td = mcalc.dewpoint_from_relative_humidity(T*units.degC, RH/100).m
    Vars['Td'] = Td
    
    ##add U, V
    ws = Vars['Ws'][:]
    wd = Vars['Wd'][:]
    U = -sin(wd/180.*pi)*ws
    V = -cos(wd/180.*pi)*ws
    Vars['U'] = U
    Vars['V'] = V
    
    return Vars