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
import json as jsn

## bugs box
"""




# """


__all__ = [
		'get_data',
		'plot',
	]



# parameter
cur_file_path = dirname(realpath(__file__))
with open(pth(cur_file_path,'metadata.json'),'r') as f:
	meta_dt = jsn.load(f)

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
		self.meta  = meta_dt['GRIMM']
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

			_tm_list = []
			for _ in _temp['Date/time']:
				try:
					if '\u4e0a\u5348' in _:
						_tm_list.append(dtm.strptime(_.replace('\u4e0a\u5348','AM'),'%Y/%m/%d %p %X'))
					else:
						_tm_list.append(dtm.strptime(_.replace('\u4e0b\u5348','PM'),'%Y/%m/%d %p %X')+dtmdt(hours=12))
				except:
						_tm_list.append(dtm.strptime(_,'%Y/%m/%d'))

			_temp['Date/time'] = _tm_list
			_temp = _temp.set_index('Date/time')
			_temp.columns = array([ _key.split('-')[0].strip('> um') for _key in list(_temp.keys()) ]).astype(float)
			
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
		## read raw data
		f_list = []
		for file in listdir(self.path):
			if '.txt' not in file.lower(): continue
			print(f"\r\t\treading {file}",end='')

			f_list = self.__raw_reader(f_list,file)
		print()

		# fout = self.__raw_process(f_list,dt_freq)
		fout = self.__raw_process(f_list)


		##=================================================================================================================
		## dump pickle file
		with open(pth(self.path,self.pkl_nam),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		return fout



	## get process data
	def get_data(self,start=None,final=None,mean_freq=None):

		## get dataframe data and process to wanted time range
		_freq = mean_freq if mean_freq is not None else '6T'
		self.__time = (start,final) if start is not None else self.__time

		return self.__reader().resample(_freq).mean().reindex(date_range(self.__time[0],self.__time[-1],freq=_freq))

	def plot(self,fig_path='.',start=None,final=None,mean_freq=None,tick_freq='6h'):

		from matplotlib.colors import LogNorm
		from matplotlib.pyplot import subplots, close, show

		## plot time series
		## make picture dir
		save_path = pth(fig_path,'GRIMM')
		mkdir(save_path) if not exists(save_path) else None

		## get data
		dt = self.get_data(start,final,mean_freq)

		## plot (T, Td), pressure, uv wind
		## parameter
		fs = 13.
		x_tick = dt.asfreq(tick_freq).index
		x_tick_lab = x_tick.strftime('%Y-%m-%d%n%X')

		setting = self.meta

		## plot
		fig, ax = subplots(figsize=(12,6),dpi=150.)
		pm = ax.pcolormesh(dt.index,dt.keys(),dt.T,cmap='jet',norm=LogNorm(vmin=setting['vmin'],vmax=setting['vmax']),
						   shading='auto')
		ax.hlines(2.5,dt.index[0],dt.index[-1],color='#000000',ls='--')
		ax.hlines(10.,dt.index[0],dt.index[-1],color='#000000',ls='--')

		box = ax.get_position()
		ax.set_position([box.x0,box.y0+0.02,box.width,box.height])
		cax = fig.add_axes([.92,box.y0+0.02,.015,box.height])
		
		cb = fig.colorbar(pm,cax=cax)
		
		ax.tick_params(which='major',length=6.,labelsize=fs-2.)
		ax.tick_params(which='minor',length=3.5)
		cb.ax.tick_params(which='major',length=5.,labelsize=fs-2.)
		cb.ax.tick_params(which='minor',length=2.5)
		ax.set(xticks=x_tick,yscale='log')
		
		ax.set_xticklabels(x_tick_lab)
		
		ax.set_xlabel('Time',fontsize=fs)
		ax.set_ylabel('Diameter ($\mu m$)',fontsize=fs)
		cb.ax.set_title('number conc.\n(#/$m^3$/$\Delta log D_p$)',fontsize=fs-2.)
		
		fig.suptitle(f'GRIMM data ({mean_freq} ave.)',fontsize=fs+2.,style='italic')

		# show()
		fig.savefig(pth(save_path,f'GRIMM_{dt.index[0].strftime("%Y%m%d%H%M")}-{dt.index[-1].strftime("%Y%m%d%H%M")}.png'))
		close()



		return dt













