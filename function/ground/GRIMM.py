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
		with open(pth(self.path,_file),'r',errors='ignore') as f:
			_temp = read_table(f,skiprows=1)
			# print(_temp)

			# breakpoint()

			_tm_list = []
			for _ in _temp['Date/time']:
				try:
					if '\u4e0a\u5348' in _:
						_tm_list.append(dtm.strptime(_.replace('\u4e0a\u5348','AM'),'%Y/%m/%d %p %X'))
					else:
						_tm_list.append(dtm.strptime(_.replace('\u4e0b\u5348','PM'),'%Y/%m/%d %p %X')+dtmdt(hours=12))
				except:
						_tm_list.append(dtm.strptime(_,'%Y/%m/%d'))

			_temp['Time'] = _tm_list
			
			# breakpoint()
			# _time = _temp['Time'].apply(lambda _: dtm.strptime(_,'%Y/%m/%d %p %X')).copy()
			
			_flist.append(_temp.set_index('Time').resample('6T').mean())



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







