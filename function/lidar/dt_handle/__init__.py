# initial function 
# version : 

# target : 
# 1. read data and process

from datetime import datetime as dtm
from os import listdir, mkdir
from os.path import join as pth, exists, dirname, realpath
import pickle as pkl
from numpy import array, nan
from pandas import date_range, concat
import json as jsn

## bugs box
"""




# """


__all__ = [
		'NDU',
		'SSC',
		'RCEC',
		'TORI',
	]


# parameter
cur_file_path = dirname(realpath(__file__))
with open(pth(cur_file_path,'metadata.json'),'r') as f:
	meta_dt = jsn.load(f)

# class
## parant class (read file)
## list the file in the path and 
## read pickle file if it exisits, else read raw data and dump the pickle file
class lidar_reader:

	## parameter
	nam = None

	## initial setting
	## input path and start time, final time
	## because the pickle file will be generated after read raw data first time, 
	## if want to reread the rawdata, please set 'reser=True'
	def __init__(self,_path,_sta=None,_fin=None,reset=False):
		print(f'\n{self.nam} lidar')
		print('='*65)
		print(f"Reading file and process data")

		if (_sta is None)&(reset): raise ValueError('\n\n\33[91mYou should input start time and final time if "reset = True"\33[0m')

		## class parameter
		self.index = lambda _freq: date_range(_sta,_fin,freq=_freq)
		self.path  = _path
		self.reset = reset
		self.meta  = meta_dt['lidar'][self.nam]
		self.pkl_nam = f'{self.nam.lower()}.pkl'
		self.__time  = (_sta,_fin)
		
		# print(f" from {_sta.strftime('%Y-%m-%d %X')} to {_fin.strftime('%Y-%m-%d %X')}")
		print('='*65)
		print(f"{dtm.now().strftime('%m/%d %X')}")

	def __raw_reader(self,_flist,_file):
		## customize each instrument
		## read one file
		return None

	def __raw_process(self,_df,_freq):
		## customize each instrument
		# breakpoint()
		out = _df.resample(_freq).mean().reindex(self.index(_freq))
		return out

	## read raw data
	def __reader(self):

		## read pickle if pickle file exisits and 'reset=False' or process raw data
		if (self.pkl_nam in listdir(self.path))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle of {self.nam} lidar")
			with open(pth(self.path,self.pkl_nam),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of {self.nam} lidar and process raw data")

		##=================================================================================================================
		## metadata parameter
		ext_nam, dt_freq, height, col_fun, col_nam, out_nam, oth_col = self.meta.values()

		## read raw data
		_df_con = None
		
		for file in listdir(self.path):
			if ext_nam not in file.lower(): continue
			print(f"\r\t\treading {file}",end='')

			_df = self.__raw_reader(file)

			if _df is not None:
				_df_con = concat([_df_con,_df]) if _df_con is not None else _df

		## concat the concated list
		df = self.__raw_process(_df_con,dt_freq)
		print()

		##=================================================================================================================
		## classify data
		## use dictionary to store data
		fout = {}
		for col, nam in zip(col_nam,out_nam):
			_df = df[[ eval(col_fun)(h,col) for h in height ]].copy()

			_df.columns = array(height).astype(int)
			_df[0] = 0

			fout[nam] = _df[array([0]+height).astype(int)]







		## process other parameter
		if oth_col is not None:
			df.rename(columns=oth_col,inplace=True)
			fout['other'] = df[list(oth_col.values())].copy()

		##=================================================================================================================
		## dump pickle file
		with open(pth(self.path,self.pkl_nam),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		return fout

	## get process data
	def get_data(self,start=None,final=None,mean_freq=None):

		## get dataframe data and process to wanted time range
		_freq = mean_freq if mean_freq is not None else self.meta['freq']
		self.__time = (start,final) if start is not None else self.__time

		_out = {}
		for _nam, _val in self.__reader().items():

			if ('ws' in _nam)|('wd' in _nam):
				_out[_nam] = _val.resample(self.meta['freq']).mean().asfreq(_freq).reindex(date_range(self.__time[0],self.__time[-1],freq=_freq))
			else:
				_out[_nam] = _val.resample(_freq).mean().reindex(date_range(self.__time[0],self.__time[-1],freq=_freq))

		## add data name
		_out['nam'] = f'{self.nam}_lidar'

		return _out




