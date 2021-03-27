# func of main
# version : 

# target : 
# 1. read data and process

from datetime import datetime as dtm
from os import listdir, mkdir
from os.path import join as pth, exists
import pickle as pkl
import numpy as n
from pandas import read_csv, read_excel, read_table, date_range, concat
import json as jsn

## bugs box
"""




# """


# parameter
with open('metadata.json','r') as f:
	meta_dt = jsn.load(f)

# class
## parant class (read file)
## list the file in the path and 
## read pickle file if it exisits, else read raw data and dump the pickle file
class lidar_reader:

	## initial setting
	## input path and start time, final time
	## because the pickle file will be generated after read raw data first time, if want to reread the rawdata, please set 'reser=True'
	def __init__(self,_path,_sta,_fin,_nam,_reset=False):
		print(f'\n{_nam} lidar')
		print('='*65)
		print(f"Reading file and process data")

		## class parameter
		self.index = lambda _freq: date_range(_sta,_fin,freq=_freq)
		self.path  = _path
		self.reset = _reset
		self.meta  = meta_dt['lidar'][_nam]
		self.nam   = _nam
		self.pkl_nam = f'{_nam.lower()}.pkl'
		
		print(f" from {_sta.strftime('%Y-%m-%d %X')} to {_fin.strftime('%Y-%m-%d %X')}")
		print('='*65)
		print(f"{dtm.now().strftime('%m/%d %X')}")

	def __raw_reader(self,_flist,_file):
		## customize each instrument
		## read one file
		return None

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
		f_list = []
		for file in listdir(self.path):
			if ext_nam not in file: continue
			print(f"\r\t\treading {file}",end='')

			f_list = self.__raw_reader(f_list,file)
		print()

		df = concat(f_list).reindex(self.index(dt_freq))

		##=================================================================================================================
		## classify data
		## use dictionary to store data
		fout = {}
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = df[[ eval(col_fun)(h,col) for h in height ]]
			fout[nam].columns = n.array(height).astype(int)

		## process other parameter
		if oth_col is not None:
			df.rename(columns=oth_col,inplace=True)
			fout['other'] = df[list(oth_col.values())]

		##=================================================================================================================
		## dump pickle file
		with open(pth(self.path,self.pkl_nam),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		return fout

	## get process data
	def get_data(self):
		return self.__reader()

# sub class
## lidar NDU
## National Defense University
## extension : .csv
## height 	 : 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
## frequence : 1s
## variable  : u, v, w, ws, wd ; 
##			   temp, RH, pressure, Az
class lidar_NDU(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='NDU',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:
			_flist.append(read_csv(f,skiprows=1,parse_dates=['Time'],na_values=[99.9,999.9],
								   date_parser=lambda _: dtm.strptime(_,'%Y%m%d_%X.%f')).set_index('Time').resample('1s').mean())		
		return _flist

## lidar SSC
## Smartec Scientific Corp
## extension : .xlsx
## height 	 : 40, 45, 50, 55, 60, 65, 70, 75, 80, 100, 120, 140
## frequence : 1 min
## variable  : ws, ws_disp, wd, ws_max, z_ws, z_ws_disp, z_ws_std, cnr, cnr_min, Dopp Spect Broad, dt_ava ; 
##			   None
class lidar_SSC(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='SSC',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'rb') as f:
			_flist.append(read_excel(f,parse_dates=['Timestamp (end of interval)']
									 ).set_index('Timestamp (end of interval)').resample('1T').mean())
		return _flist

## lidar RCEC
## Research Center of Environmental Changes
## extension : .csv
## height 	 : 51, 77, 103, ... ,4988, 5014 (60m ~ 5820m * sin(60) ) 
## frequence : 5 min
## variable  : ws, wd, SNR, dtObtRate, std, ws_max, ws_max, z_ws, z_ws_std ; 
##			   temp, RH, pressure
class lidar_RCEC(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='RCEC',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:
			_flist.append(read_csv(f,skiprows=1,parse_dates=['Date_time'],na_values=[99.9,999],
								   date_parser=lambda _: dtm.strptime(_,'%Y%m%d %X')).set_index('Date_time').resample('5T').mean())
		return _flist


## lidar TORI
## Taiwan Ocean Research Institute
## extension : .sta
## height 	 : 40, 45, 55, 65, 75, 85, 95, 115, 135, 155, 175, 195
## frequence : 1 min
## variable  : ws, ws_disp, wd, ws_max, z_ws, z_ws_disp, z_ws_std, cnr, cnr_min, Dopp Spect Broad, dt_ava ; 
##			   temp, ext temp, RH, pressure, Vbatt
class lidar_TORI(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='TORI',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:
			_flist.append(read_table(f,skiprows=41,parse_dates=['Timestamp (end of interval)']
									 ).set_index('Timestamp (end of interval)').resample('1T').mean())
		return _flist


# test
start_dtm = dtm(2020,11,20,0,0,0)
final_dtm = dtm(2020,11,21,0,0,0)
path = pth('..','data','Lidar_Sunsing_NDU_testdata')
reader = lidar_NDU(path,start_dtm,final_dtm,reset=True)
dt = reader.get_data()

start_dtm = dtm(2015,1,23,12,30,0)
final_dtm = dtm(2015,1,23,15,30,0)
path = pth('..','data','Lidar_Sunsing_SSC_testdata')
reader = lidar_SSC(path,start_dtm,final_dtm,reset=True)
dt1 = reader.get_data()

start_dtm = dtm(2020,11,27,0,0,0)
final_dtm = dtm(2020,11,28,0,0,0)
path = pth('..','data','Lidar_Sunsing_RCEC_testdata')
reader = lidar_RCEC(path,start_dtm,final_dtm,reset=True)
dt2 = reader.get_data()

start_dtm = dtm(2014,12,29,1,30,0)
final_dtm = dtm(2014,12,29,2,0,0)
path = pth('..','data','Lidar_Sunsing_TORI_testdata')
reader = lidar_TORI(path,start_dtm,final_dtm,reset=True)
dt3 = reader.get_data()



## radiosonde
'''

	def radiosonde_NTU(self,start,final):
		## read pickle or process raw data
		if ('radio_ntu.pkl' in listdir(self.path_radio_NTU))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of NTU radiosonde")
			with open(pth(self.path_radio_NTU,'radio_ntu.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of NTU radiosonde")

		## read raw data
		fList = []
		for file in listdir(self.path_radio_NTU):
			if '.txt' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_radio_NTU,file),'r',encoding='utf-8',errors='ignore') as f:
				fList.append(read_table(f,skiprows=[0,1,2,3,5],delimiter='\s+').set_index('HeightMSL'))
		print()
		
		fout = {}
		for time, _df in zip(self.index(start,final,'1d'),fList):
			fout[time.strftime('%Y/%m/%d')] = _df


		with open(pth(self.path_radio_NTU,'radio_ntu.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		## process different height
		# height = [40,45,50,55,60,65,70,75,80,100,120,140]
		# col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction (?','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   # 'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		# out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		# fout = {}
		# for col, nam in zip(col_nam,out_nam):
			# fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			# fout[nam].columns = height

		return fout

	def radiosonde_RCEC(self,start,final):
		## read pickle or process raw data
		if ('radio_rcec.pkl' in listdir(self.path_radio_RCEC))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of RCEC radiosonde")
			with open(pth(self.path_radio_RCEC,'radio_rcec.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of RCEC radiosonde")

		## read raw data
		fList = []
		for file in listdir(self.path_radio_RCEC):
			if '.txt' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_radio_RCEC,file),'r',encoding='utf-8',errors='ignore') as f:
				fList.append(read_table(f,skiprows=2,delimiter=',\s+|\s+',engine='python').set_index('Height'))
		print()
		
		fout = {}
		for time, _df in zip(self.index(start,final,'1d'),fList):
			fout[time.strftime('%Y/%m/%d')] = _df

		with open(pth(self.path_radio_RCEC,'radio_rcec.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		## process different height
		# height = [40,45,50,55,60,65,70,75,80,100,120,140]
		# col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction (?','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   # 'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		# out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		# fout = {}
		# for col, nam in zip(col_nam,out_nam):
			# fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			# fout[nam].columns = height

		return fout




# start_dtm = dtm(2021,3,16,0,0,0)
# final_dtm = dtm(2021,3,16,0,0,0)
# dt = reader.radiosonde_RCEC(start_dtm,final_dtm)


# start_dtm = dtm(2021,3,16,0,0,0)
# final_dtm = dtm(2021,3,16,0,0,0)
# dt = reader.radiosonde_NTU(start_dtm,final_dtm)


# '''
