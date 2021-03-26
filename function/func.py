# func of main
# version : 

# target : 
# 1. read data of 4 lidars

from datetime import datetime as dtm
from os import listdir, mkdir
from os.path import join as pth, exists
import pickle as pkl
import numpy as n
import pandas as pd
#from matplotlib.pyplot import subplots, close, show
#import matplotlib.pyplot as pl
from itertools import combinations as comb


# class
## read file
class lidar_reader:
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
		self.reset	= default['reset']
		
		print('='*50)
		print(f"{dtm.now().strftime('%m/%d %X')}")

	## reader of National Defense University
	def read_NDU(self,start,final):

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
	def read_RCEC(self,start,final):

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
	def read_TORI(self,start,final):
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

		return fout

	## reader of Smartec Scientific Corp
	def read_SSC(self,start,final):
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
		# breakpoint()
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

		return fout
		
		## process other parameter





setting = {'path_NDU'  : pth('..','data','Lidar_Sunsing_NDU_testdata'),
		   'path_SSC'  : pth('..','data','Lidar_Sunsing_SSC_testdata'),
		   'path_TORI' : pth('..','data','Lidar_Sunsing_TORI_testdata'),
		   'path_RCEC' : pth('..','data','Lidar_Sunsing_RCEC_testdata'),
		   'reset'	   : True
			}


reader = lidar_reader(set_dic=setting)



start_dtm = dtm(2020,11,20,0,0,0)
final_dtm = dtm(2020,11,21,0,0,0)

dt1 = reader.read_NDU(start_dtm,final_dtm)


start_dtm = dtm(2020,11,27,0,0,0)
final_dtm = dtm(2020,11,28,0,0,0)

dt2 = reader.read_RCEC(start_dtm,final_dtm)

start_dtm = dtm(2014,12,29,1,30,0)
final_dtm = dtm(2014,12,29,2,0,0)

dt3 = reader.read_TORI(start_dtm,final_dtm)

start_dtm = dtm(2015,1,23,12,30,0)
final_dtm = dtm(2015,1,23,15,30,0)

dt = reader.read_SSC(start_dtm,final_dtm)


