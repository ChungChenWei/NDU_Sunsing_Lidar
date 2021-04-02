
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
def plot_all(dt_dic,fig_path='.',freq='5h'):


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
	
	_plot('ws')
	# _plot('z_ws')

	## plot ws wd quiver
	def _plot_quiver():
		## parameter
		fs = 13.
		setting = meta[quiver]

		## plot ws, wd pcolormesh
		dt = dt_dic[_nam]

		## plot quiver with cmap, same length quivers



		##





