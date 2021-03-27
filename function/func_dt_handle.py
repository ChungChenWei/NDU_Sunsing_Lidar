# func of main
# version : 

# target : 
# 1. read data and process

from datetime import datetime as dtm
from os import listdir, mkdir
from os.path import join as pth, exists
import pickle as pkl
import numpy as n
import pandas as pd
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
		self.index = lambda _freq: pd.date_range(_sta,_fin,freq=_freq)
		self.path  = _path
		self.reset = _reset
		self.meta  = meta_dt['lidar'][_nam]
		self.nam   = _nam
		self.pkl_nam = f'{_nam.lower()}.pkl'
		
		print(f" from {_sta.strftime('%Y-%m-%d %X')} to {_fin.strftime('%Y-%m-%d %X')}")
		print('='*65)
		print(f"{dtm.now().strftime('%m/%d %X')}")

	def _raw_reader(self,_flist,_file):
		## customize each instrument
		## read one file
		print('not cool')
		return None

	# def __prcs_data(self,_df):
		# customize each instrument
		# process all file
		# return None

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

		## metadata parameter
		ext_nam, dt_freq, height, col_fun, col_nam, out_nam, oth_col = self.meta.values()

		## read raw data
		f_list = []
		for file in listdir(self.path):
			if ext_nam not in file: continue
			print(f"\r\t\treading {file}",end='')

			f_list = self._raw_reader(f_list,file)


			# breakpoint()
		print()

		df = pd.concat(f_list).reindex(self.index(dt_freq))
		
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


		with open(pth(self.path,self.pkl_nam),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		return fout


	def get_data(self):
		return self.__reader()


class lidar_NDU(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='NDU',_reset=reset)


	def _raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:
			_flist.append(pd.read_csv(f,skiprows=1,parse_dates=['Time'],na_values=[99.9,999.9],
									  date_parser=lambda _: dtm.strptime(_,'%Y%m%d_%X.%f')).set_index('Time').resample('1s').mean())		
		return _flist




start_dtm = dtm(2020,11,20,0,0,0)
final_dtm = dtm(2020,11,21,0,0,0)
path = pth('..','data','Lidar_Sunsing_NDU_testdata')

reader = lidar_NDU(path,start_dtm,final_dtm,reset=True)

dt = reader.get_data()




























'''

ndu
		## process different height

		# height   = [100,200,300,400,500,600,700,800,900,1000]
		# col_func = "lambda _h, _col: f'H{int(_h/100)}_{_col}'"
		# col_nam  = ['u','v','w','ws','wd']
		# out_nam  = ['u','v','w','ws','wd']






		fout = {}
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = _df[[ eval(col_func)(h,col) for h in height ]]
			fout[nam].columns = n.array(height).astype(int)



		## process other parameter
		if oth_col is not None:
			df.rename(columns=oth_col,inplace=True)
			fout['other'] = df[[list(oth_col.values())]]




{'Temp.':'temp','Humin.':'RH','Pressure.':'pressure','Az':'az'}

		height = []
		for col in _df.keys():
			if col in ['Temperature', 'Humidity', 'Pressure']: continue
			height.append(col.split('m ')[0]) if col.split('m ')[0] not in height else None



rcec

		fout = {}
		col_nam = ['WindSpeed','WindDirection','MeanSNR(dB)','DataObtainRate','StdDev','Max WindSpeed','Min WindSpeed','ZWind','ZWind StdDev']
		out_nam = ['ws','wd','SNR','dtObtRate','std','ws_max','ws_max','z_ws','z_ws_std']
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			fout[nam].columns = n.array(height).astype(int)

		## process other parameter
		_df.rename(columns={'Temperature':'temp','Humidity':'RH','Pressure':'pressure'},inplace=True)
		fout['other'] = _df[['temp','RH','pressure']]



tori
		## process different height
		## CNR : carrier to noise ratio
		height = [40,45,55,65,75,85,95,115,135,155,175,195]
		col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction ()','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		fout = {}
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			fout[nam].columns = height
		
		## process other parameter
		_df.rename(columns={'Int Temp (C)':'temp','Ext Temp (C)':'ext temp','Wiper count':'wiper count',
							'Rel Humidity (%)':'RH','Pressure (hPa)':'pressure','Vbatt (V)':'Vbatt'},inplace=True)
		fout['other'] = _df[['temp','ext temp','pressure','RH','wiper count','Vbatt']]

		with open(pth(self.path_TORI,'tori.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)


ssc

		## process different height
		## CNR : carrier to noise ratio
		height = [40,45,50,55,60,65,70,75,80,100,120,140]
		col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction (?','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		fout = {}
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			fout[nam].columns = height









'''






class reader:
	def __init__(self,set_dic={}):
		print('\n'+'='*50)
		print(f"Reading file and process data")

		## default parameter
		default = {'path_NDU'  : 'NDU/',
				   'path_RCEC' : 'RCEC/',
				   'path_TORI' : 'TORI/',
				   'path_SSC'  : 'SSC/',
				   'reset'	   : False,}
		default.update(set_dic)

		## class parameter
		self.index = lambda _start, _final, _freq: pd.date_range(_start,_final,freq=_freq)

		self.path_NDU	= default['path_NDU']
		self.path_RCEC	= default['path_RCEC']
		self.path_TORI	= default['path_TORI']
		self.path_SSC	= default['path_SSC']
		self.path_radio_NTU	 = default['path_radio_NTU']
		self.path_radio_RCEC = default['path_radio_RCEC']
		self.path_SSC	= default['path_SSC']
		self.path_SSC	= default['path_SSC']
		self.reset	= default['reset']
		
		print('='*50)
		print(f"{dtm.now().strftime('%m/%d %X')}")

	## reader of National Defense University
	def lidar_NDU(self,start,final):

		## read pickle or process raw data
		if ('ndu.pkl' in listdir(self.path_NDU))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of NDU lidar")
			with open(pth(self.path_NDU,'ndu.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of NDU lidar")

		## read raw data
		fList = []
		for file in listdir(self.path_NDU):
			if '.csv' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_NDU,file),'r',encoding='utf-8',errors='ignore') as f:
				fList.append(pd.read_csv(f,skiprows=1,parse_dates=['Time'],na_values=[99.9,999.9],
							 date_parser=lambda _: dtm.strptime(_,'%Y%m%d_%X.%f')).set_index('Time').resample('1s').mean())
		print()
		_df = pd.concat(fList).reindex(self.index(start,final,'1s'))
		
		## process different height
		fout = {}
		for nam in ['u','v','w','ws','wd']:
			fout[nam] = _df[[ '_'.join([_h,nam]) for _h in [ f'H{_:d}' for _ in range(1,11) ] ]]
			fout[nam].columns = range(100,1100,100)

		## process other parameter
		_df.rename(columns={'Temp.':'temp','Humin.':'RH','Pressure.':'pressure','Az':'az'},inplace=True)
		fout['other'] = _df[['temp','RH','pressure','az']]


		with open(pth(self.path_NDU,'ndu.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)


		return fout

	## reader of Research Center of Environmental Changes
	def lidar_RCEC(self,start,final):

		## read pickle or process raw data
		if ('rcec.pkl' in listdir(self.path_RCEC))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of RCEC lidar")
			with open(pth(self.path_RCEC,'rcec.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of RCEC lidar")

		## read raw data
		fList = []
		for file in listdir(self.path_RCEC):
			if '.csv' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_RCEC,file),'r',encoding='utf-8',errors='ignore') as f:
				fList.append(pd.read_csv(f,skiprows=1,parse_dates=['Date_time'],na_values=[99.9,999],
							 date_parser=lambda _: dtm.strptime(_,'%Y%m%d %X')).set_index('Date_time').resample('5T').mean())
		print()
		_df = pd.concat(fList).reindex(self.index(start,final,'5T'))

		## process different height
		height = []
		for col in _df.keys():
			if col in ['Temperature', 'Humidity', 'Pressure']: continue
			height.append(col.split('m ')[0]) if col.split('m ')[0] not in height else None


		fout = {}
		col_nam = ['WindSpeed','WindDirection','MeanSNR(dB)','DataObtainRate','StdDev','Max WindSpeed','Min WindSpeed','ZWind','ZWind StdDev']
		out_nam = ['ws','wd','SNR','dtObtRate','std','ws_max','ws_max','z_ws','z_ws_std']
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			fout[nam].columns = n.array(height).astype(int)

		## process other parameter
		_df.rename(columns={'Temperature':'temp','Humidity':'RH','Pressure':'pressure'},inplace=True)
		fout['other'] = _df[['temp','RH','pressure']]

		with open(pth(self.path_RCEC,'rcec.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		return fout

	## reader of Taiwan Ocean Research Institute
	def lidar_TORI(self,start,final):
		## read pickle or process raw data
		if ('tori.pkl' in listdir(self.path_TORI))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of TORI lidar")
			with open(pth(self.path_TORI,'tori.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of TORI lidar")

		## read raw data
		fList = []
		for file in listdir(self.path_TORI):
			if '.sta' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_TORI,file),'r',encoding='utf-8',errors='ignore') as f:

				fList.append(pd.read_table(f,skiprows=41,
							 parse_dates=['Timestamp (end of interval)']).set_index('Timestamp (end of interval)').resample('1T').mean())
		print()
		_df = pd.concat(fList).reindex(self.index(start,final,'1T'))

		## process different height
		## CNR : carrier to noise ratio
		height = [40,45,55,65,75,85,95,115,135,155,175,195]
		col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction ()','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		fout = {}
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			fout[nam].columns = height
		
		## process other parameter
		_df.rename(columns={'Int Temp (C)':'temp','Ext Temp (C)':'ext temp','Wiper count':'wiper count',
							'Rel Humidity (%)':'RH','Pressure (hPa)':'pressure','Vbatt (V)':'Vbatt'},inplace=True)
		fout['other'] = _df[['temp','ext temp','pressure','RH','wiper count','Vbatt']]

		with open(pth(self.path_TORI,'tori.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		return fout

	## reader of Smartec Scientific Corp
	def lidar_SSC(self,start,final):
		## read pickle or process raw data
		if ('ssc.pkl' in listdir(self.path_SSC))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of SSC lidar")
			with open(pth(self.path_SSC,'ssc.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of SSC lidar")

		## read raw data
		fList = []
		for file in listdir(self.path_SSC):
			if '.xlsx' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_SSC,file),'rb') as f:
				fList.append(pd.read_excel(f,parse_dates=['Timestamp (end of interval)']).set_index('Timestamp (end of interval)').resample('1T').mean())
		print()
		_df = pd.concat(fList).reindex(self.index(start,final,'1T'))

		## process different height
		## CNR : carrier to noise ratio
		height = [40,45,50,55,60,65,70,75,80,100,120,140]
		col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction (?','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		fout = {}
		for col, nam in zip(col_nam,out_nam):
			fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			fout[nam].columns = height

		with open(pth(self.path_SSC,'ssc.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		return fout

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
				fList.append(pd.read_table(f,skiprows=[0,1,2,3,5],delimiter='\s+').set_index('HeightMSL'))
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
				fList.append(pd.read_table(f,skiprows=2,delimiter=',\s+|\s+',engine='python').set_index('Height'))
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



setting = {'path_NDU'  : pth('..','data','Lidar_Sunsing_NDU_testdata'),
		   'path_SSC'  : pth('..','data','Lidar_Sunsing_SSC_testdata'),
		   'path_TORI' : pth('..','data','Lidar_Sunsing_TORI_testdata'),
		   'path_RCEC' : pth('..','data','Lidar_Sunsing_RCEC_testdata'),
		   'path_radio_NTU'  : pth('..','data','Radiosonde_NTU'),
		   'path_radio_RCEC' : pth('..','data','Radiosonde_RCEC'),
		   'reset'	   : False
			}

# reader = reader(set_dic=setting)

'''

start_dtm = dtm(2020,11,20,0,0,0)
final_dtm = dtm(2020,11,21,0,0,0)
dt1 = reader.lidar_NDU(start_dtm,final_dtm)

start_dtm = dtm(2020,11,27,0,0,0)
final_dtm = dtm(2020,11,28,0,0,0)
dt2 = reader.lidar_RCEC(start_dtm,final_dtm)

start_dtm = dtm(2014,12,29,1,30,0)
final_dtm = dtm(2014,12,29,2,0,0)
dt3 = reader.lidar_TORI(start_dtm,final_dtm)

start_dtm = dtm(2015,1,23,12,30,0)
final_dtm = dtm(2015,1,23,15,30,0)
dt = reader.lidar_SSC(start_dtm,final_dtm)

start_dtm = dtm(2021,3,16,0,0,0)
final_dtm = dtm(2021,3,16,0,0,0)
dt = reader.radiosonde_NTU(start_dtm,final_dtm)
# '''



# start_dtm = dtm(2021,3,16,0,0,0)
# final_dtm = dtm(2021,3,16,0,0,0)
# dt = reader.radiosonde_RCEC(start_dtm,final_dtm)

