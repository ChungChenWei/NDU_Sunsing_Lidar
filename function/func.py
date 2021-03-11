# func of main
# version : 

# target : 
# 1. read data of 4 lidars

from datetime import datetime as dtm
from os import listdir, mkdir
from os.path import join as pth, exists
import pickle as pkl
#import numpy as n
import pandas as pd
#from matplotlib.pyplot import subplots, close, show
#import matplotlib.pyplot as pl


# class
## read file
class lidar_reader:
	def __init__(self,start,final,set_dic={}):
		print('\n'+'='*50)
		print(f"Reading file and process data")

		## default parameter
		default = {'path_NDU'  : 'NDU/',
				   'path_RCEC' : 'RCEC/',
				   'path_3'  : 'cpc/',
				   'path_4'  : 'smps/',
				   'path_output' : './',}
		default.update(set_dic)

		## class parameter
		self.start = start ## datetime object
		self.final = final ## datetime object
		self.index = lambda _freq: pd.date_range(start,final,freq=_freq)

		self.path_NDU	= default['path_NDU']
		self.path_RCEC	= default['path_RCEC']
		self.path_3	= default['path_3']
		self.path_4	= default['path_4']
		
		print(f" from {start.strftime('%Y-%m-%d %X')} to {final.strftime('%Y-%m-%d %X')}")
		print('='*50)
		print(f"{dtm.now().strftime('%m/%d %X')}")

	## reader of National Defense University
	def read_NDU(self):

		## read pickle or process raw data
		if 'ndu.pkl' in listdir(self.path_NDU): 
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
				"""
				rawDt : data, use 'Date' and 'Start Time' as index
				fList : all reading file
				"""
				fList.append(pd.read_csv(f,skiprows=1,parse_dates=['Time'],na_values=[99.9,999.9],
							 date_parser=lambda _: dtm.strptime(_,'%Y%m%d_%X.%f')).set_index('Time').resample('1s').mean())
							
			# return fList[0]
		print()
		fout = pd.concat(fList).reindex(self.index('1s'))

		with open(pth(self.path_NDU,'ndu.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)


		return fout



	## reader of Research Center of Environmental Changes
	def read_RCEC(self,):
		return None

	## forget
	def read_3(self,):
		return None

	## forget
	def read_4(self,):
		return None






setting = {'path_NDU' : pth('..','NDU_Sunsing_Lidar','Lidar_Sunsing_NDU_testdata')}
start_dtm = dtm(2020,11,20,0,0,0)
final_dtm = dtm(2020,11,21,0,0,0)


reader = lidar_reader(start_dtm,final_dtm,set_dic=setting)
nduDt = reader.read_NDU()