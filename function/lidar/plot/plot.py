
# plot function

from matplotlib.pyplot import subplots, close, show
from matplotlib import rcParams
# rcParams['pcolor.shading'] = 'flat'

import numpy as n

# from datetime import datetime as dtm
from os import mkdir
from os.path import join as pth, exists, dirname, realpath
# import pickle as pkl
# from numpy import array, nan
# from pandas import date_range, concat
import json as jsn

## bugs box
"""


# """


__all__ = [
		'plot_all',
	]


# parameter
cur_file_path = dirname(realpath(__file__))
with open(pth(cur_file_path,'metadata.json'),'r') as f:
	meta_dt = jsn.load(f)




## plot all variable
def plot_all(dt_dic,fig_path='.',dt_freq='30T',tick_freq='5h'):

	## parameter
	dt_nam = dt_dic['nam'].split('_')[0]
	meta = meta_dt[dt_nam]

	## make picture dir
	save_path = pth(fig_path,dt_nam)
	mkdir(save_path) if not exists(save_path) else None

	## function
	def _plot_pcolor(_nam):

		## parameter
		fs = 13.
		setting = meta[_nam]

		## plot ws, wd pcolormesh
		dt = dt_dic[_nam]

		dt.replace(0.,n.nan,inplace=True)

		x_tick = dt.asfreq(freq).index
		x_tick_lab = x_tick.strftime('%Y-%m-%d%n%X')

		fig, ax = subplots(figsize=(12,6),dpi=150.)
		pm = ax.pcolormesh(dt.index,dt.keys(),dt[:-1].T[:-1],cmap='jet',vmin=setting['vmin'],vmax=setting['vmax'])

		box = ax.get_position()
		ax.set_position([box.x0,box.y0+0.02,box.width,box.height])
		cax = fig.add_axes([.92,box.y0+0.02,.015,box.height])
		
		cb = fig.colorbar(pm,cax=cax)
		
		ax.tick_params(which='major',length=6.,labelsize=fs-2.)
		ax.tick_params(which='minor',length=3.5)
		cb.ax.tick_params(which='major',length=5.,labelsize=fs-2.)
		cb.ax.tick_params(which='minor',length=2.5)
		ax.set(xticks=x_tick,ylim=(setting['ylim_bot'],setting['ylim_top']))
		
		ax.set_xticklabels(x_tick_lab)
		
		ax.set_xlabel('Time',fontsize=fs)
		ax.set_ylabel('Height (m)',fontsize=fs)
		cb.ax.set_title(setting['cb_label'],fontsize=fs-2.)
		
		fig.suptitle(f'{dt_nam.upper()} data : {_nam}',fontsize=fs+2.,style='italic')

		# show()
		fig.savefig(pth(save_path,f'{dt_nam}_{_nam}_{dt.index[0].strftime("%Y%m%d%H%M")}-{dt.index[-1].strftime("%Y%m%d%H%M")}.png'))
		close()

	## plot ws wd quiver
	def _plot_quiver():

		## function
		def wswd2uv(_ws,_wd):
			return -n.sin(_wd/180.*n.pi)*_ws, -n.cos(_wd/180.*n.pi)*_ws

		## parameter
		fs = 13.
		setting = meta['quiver']

		# breakpoint()

		dt_ws, dt_wd = dt_dic['ws'].asfreq(dt_freq)[::setting['sep']], dt_dic['wd'].asfreq(dt_freq)[::['sep']]
		
		dt_ws[dt_ws.keys()[-1]].replace(0.,n.nan,inplace=True)
		dt_wd[dt_ws.keys()[-1]].replace(0.,n.nan,inplace=True)
		dt_ws.replace(0.,.1,inplace=True)

		_u, _v = wswd2uv(1.,dt_wd)

		# breakpoint()

		x_tick = dt_ws.asfreq(freq).index
		x_tick_lab = x_tick.strftime('%Y-%m-%d%n%X')

		## plot quiver with cmap, same length quiverssss
		fig, ax = subplots(figsize=(12,6),dpi=150.)

		qv = ax.quiver(_u.index,_u.keys(),_u.T,_v.T,dt_ws.T,cmap='jet',scale=50.)

		box = ax.get_position()
		ax.set_position([box.x0,box.y0+0.02,box.width,box.height])
		cax = fig.add_axes([.92,box.y0+0.02,.015,box.height])
		
		cb = fig.colorbar(qv,cax=cax)
		
		ax.tick_params(which='major',length=6.,labelsize=fs-2.)
		ax.tick_params(which='minor',length=3.5)
		cb.ax.tick_params(which='major',length=5.,labelsize=fs-2.)
		cb.ax.tick_params(which='minor',length=2.5)

		ax.set(xticks=x_tick,ylim=(setting['ylim_bot'],setting['ylim_top']))
		ax.set_xticklabels(x_tick_lab)
		
		ax.set_xlabel('Time',fontsize=fs)
		ax.set_ylabel('Height (m)',fontsize=fs)
		cb.ax.set_title(setting['cb_label'],fontsize=fs-2.)
		
		fig.suptitle(f'{dt_nam.upper()} data : wind speed and Wind direction',fontsize=fs+2.,style='italic')

		# show()
		fig.savefig(pth(save_path,f'{dt_nam}_wswd_{dt_ws.index[0].strftime("%Y%m%d%H%M")}-{dt_ws.index[-1].strftime("%Y%m%d%H%M")}.png'))
		close()


	## plot
	_plot_quiver()
	
	_plot_pcolor('ws')
	_plot_pcolor('z_ws')




