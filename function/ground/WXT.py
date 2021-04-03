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
from pandas import read_csv, concat
from numpy import sin, cos, pi
from metpy.units import units
import metpy.calc as mcalc
from matplotlib.pyplot import subplots, close, show
import json as jsn
import pickle as pkl



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
		self.meta  = meta_dt['WXT']
		self.nam   = 'WXT'
		self.pkl_nam = f'wxt.pkl'
		self.__time  = (start,final)
		
		print(f" from {start.strftime('%Y-%m-%d %X')} to {final.strftime('%Y-%m-%d %X')}")
		print('='*65)
		print(f"{dtm.now().strftime('%m/%d %X')}")




	def __raw_reader(self,_flist,_file):
		## customize each instrument
		## read one file
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:

			_rename = {'airtemp_Avg'	 : 'T',
					   'relhumidity_Avg' : 'RH', 
					   'airpressure_Avg' : 'P', 
					   'Wsavg_Avg'		 : 'ws',
					   'Wdavg_Avg'		 : 'wd',
					   'WindDir_SD1_WVT' : 'wd_std'}

			_temp = read_csv(f,skiprows=(0,2,3),parse_dates=['TIMESTAMP']).rename(columns=_rename).set_index('TIMESTAMP')

			_temp['Td'] = mcalc.dewpoint_from_relative_humidity(_temp['T'].to_numpy(dtype=float)*units.degC,
																_temp['RH'].to_numpy(dtype=float)/100.).m
			_temp['u'] = -sin(_temp['wd']/180.*pi)*_temp['ws']
			_temp['v'] = -cos(_temp['wd']/180.*pi)*_temp['ws']

			_flist.append(_temp[list(_rename.values())+['Td','u','v']].astype(float).resample('1T').mean())

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
			if '.dat' not in file.lower(): continue
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
		_freq = mean_freq if mean_freq is not None else '1T'
		self.__time = (start,final) if start is not None else self.__time

		_temp = self.__reader().loc[self.__time[0]:self.__time[-1]]

		_out  = _temp[['ws','wd','wd_std','u','v']].asfreq(_freq)
		for _nam in ['T','RH','P','Td']: _out[_nam] = _temp[_nam].resample(_freq).mean()

		return _out


	def plot(self,fig_path='.',start=None,final=None,mean_freq=None,tick_freq='6h'):

		## make picture dir
		save_path = pth(fig_path,'WXT')
		mkdir(save_path) if not exists(save_path) else None

		## get data
		df = self.get_data(start,final,mean_freq)

		## plot (T, Td), pressure, uv wind
		## parameter
		fs = 13.
		x_tick = df.asfreq(tick_freq).index
		x_tick_lab = x_tick.strftime('%Y-%m-%d%n%X')

		## plot
		fig, axes = subplots(3,1,figsize=(10,7),dpi=150.,gridspec_kw=dict(wspace=.325,hspace=.45),sharex=False,sharey=False)

		## plot T and P
		axes[0].plot(df['Td'],color='#4cffff',label='$T_d$')

		for ax, _nam in zip(axes,['T','P']):
			setting = self.meta[_nam]
			
			ax.plot(df[_nam],color=setting['color'],label=_nam)

			ax.set(ylim=(setting['ylim_bot'],setting['ylim_top']),xticks=x_tick)
			ax.set_title(setting['title'],fontsize=fs)
			ax.set_ylabel(setting['ylabel'],fontsize=fs)
			ax.set_xticklabels('')

		axes[0].legend(framealpha=0,fontsize=fs-2.5)

		## plot uv
		ax = axes[2]
		setting = self.meta['wind']

		itv = setting['itv']
		ax.quiver(df.index[::itv],0.,df['u'][::itv],df['v'][::itv],scale=5,scale_units='inches',color='#cc99ff',
				  headwidth=2.)
		# ax.quiver(df.index[::itv],0.,df['u'][::itv],df['v'][::itv],angles='xy', scale_units='xy', scale=1.,color='#cc99ff')

		ax.set(xticks=x_tick,ylim=(-2,2),xlim=(df.index[0],df.index[-1]))
		ax.set_title(setting['title'],fontsize=fs)
		ax.set_ylabel(setting['ylabel'],fontsize=fs)

		ax.set_xticklabels(x_tick_lab)
				
		fig.text(.5,.03,'Time',ha='center',fontsize=fs)
		
		fig.suptitle('WXT data',fontsize=fs+2.,style='italic')
		fig.savefig(pth(save_path,f'WXR_{df.index[0].strftime("%Y%m%d%H%M")}-{df.index[-1].strftime("%Y%m%d%H%M")}.png'))
		# show()
		close()

		return df





    




























