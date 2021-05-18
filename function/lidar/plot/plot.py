
# plot function

from matplotlib.pyplot import subplots, close, show
import matplotlib.cm as cm
import matplotlib.colors as mc
# from matplotlib import rcParams
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
def plot_all(dt_dic,fig_path='.',tick_freq='6h',input_tick=None):



	## parameter
	dt_nam = dt_dic['nam'].split('_')[0]
	_ind = dt_dic['ws'].index
	print(f'\nPlot {dt_nam} data')

	## make picture dir
	dir_path = pth(fig_path,dt_nam)
	mkdir(dir_path) if not exists(dir_path) else None

	save_path = {}
	save_path[dt_nam] = pth(dir_path,f'{_ind[0].strftime("%Y-%m-%d %H")}_{_ind[-1].strftime("%Y-%m-%d %H")}')
	mkdir(save_path[dt_nam]) if not exists(save_path[dt_nam]) else None



	mkdir(pth(fig_path,'lidar_comp')) if not exists(pth(fig_path,'lidar_comp')) else None
	save_path['comp'] = pth(fig_path,'lidar_comp',f'{_ind[0].strftime("%Y-%m-%d %H")}_{_ind[-1].strftime("%Y-%m-%d %H")}')
	mkdir(save_path['comp']) if not exists(save_path['comp']) else None

	## function
	meta = meta_dt[dt_nam]
	def _plot_pcolor(_nam,_cmap):
		print(f'\tplot {dt_nam} : {_nam}')

		## parameter
		fs = 13.
		setting = meta[_nam]

		## plot ws, wd pcolormesh
		## parameter
		dt = dt_dic[_nam]
		dt.replace(0.,n.nan,inplace=True)

		x_tick = dt.asfreq(tick_freq).index
		x_tick_lab = x_tick.strftime('%Y-%m-%d%n%X')

		## plot
		fig, ax = subplots(figsize=(12,6),dpi=150.)
		pm = ax.pcolormesh(dt.index,dt.keys(),dt[:-1].T[:-1],cmap=_cmap,vmin=setting['vmin'],vmax=setting['vmax'])

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






	## plot quiver and vertical wind
	def _plot_quiver(fig,ax,fs,box,meta):

		## parameter
		def wswd2uv(_ws,_wd):
			return -n.sin(_wd/180.*n.pi)*_ws, -n.cos(_wd/180.*n.pi)*_ws

		cmap_bot = cm.get_cmap('RdGy',512)(n.linspace(.15,.5,512))
		cmap_top = cm.get_cmap('RdGy',512)(n.linspace(.5,1.,512))
		cmap = mc.ListedColormap(n.vstack((cmap_bot,cmap_top)))
		cmap = 'jet'


		setting = meta['quiver']
		# dt_ws, dt_wd = dt_dic['ws'].asfreq(dt_freq)[::setting['sep']], dt_dic['wd'].asfreq(dt_freq)[::setting['sep']]
		dt_ws, dt_wd = dt_dic['ws'].asfreq(setting['dt_freq']), dt_dic['wd'].asfreq(setting['dt_freq'])
		
		# dt_ws[dt_ws.keys()[0]].replace(0.,n.nan,inplace=True)
		# dt_wd[dt_ws.keys()[0]].replace(0.,n.nan,inplace=True)

		## (1) replace 0 as nan, process the by-product after interpolate
		## (2) get the mask below 2.5
		## (3) set the value as nan under mask
		## (4) get the mask out value, apply scatter plot
		dt_ws.replace(0.,n.nan,inplace=True)
		_mask = dt_ws.copy()<2.5
		dt_ws.mask(_mask,n.nan,inplace=True)
		_index, _height =n.meshgrid(dt_ws.index,dt_ws.keys())

		## change ws, wd to u, v
		## get height as y axis and get x ticks
		_u, _v = wswd2uv(1.5,dt_wd)
		height = n.array(list(dt_ws.keys())).astype(float)
		x_tick = input_tick if input_tick is not None else dt_ws.asfreq(tick_freq).index 

		## plot
		sc = ax.scatter(_index[_mask.T],_height[_mask.T],s=15,fc='None',ec='#666666',label='< 2.5 m/s')

		qv = ax.quiver(_u.index,height[::setting['sep']],_u.T[::setting['sep']],_v.T[::setting['sep']],dt_ws.T[::setting['sep']].values,
					   cmap=cmap,scale=50,clim=(setting['vmin'],setting['vmax']))
	
		cax = fig.add_axes([.92,box.y0,.015,box.height])

		cb = fig.colorbar(qv,cax=cax)
		cb.ax.tick_params(which='major',length=5.,labelsize=fs-2.)
		cb.ax.tick_params(which='minor',length=2.5)
		cb.ax.set_title(setting['cb_label'],fontsize=fs-2.)

		ax.legend(handles=[sc],framealpha=0,fontsize=fs-1.,loc=10,bbox_to_anchor=(0.1,1.025),handlelength=1.)

		return x_tick, dt_ws.index[0], dt_ws.index[-1]



	## plot z_ws pcolormesh
	def _plot_z_ws(fig,ax,fs,box,meta):

		## parameter
		setting = meta['z_ws']

		# cmap_bot = cm.get_cmap('Blues_r',512)(n.linspace(.5,1.,512))
		cmap_top = cm.get_cmap('Greys',512)(n.linspace(.45,.6,512))
		cmap_bot = cm.get_cmap('Greys',512)(n.linspace(.0,.3,512))
		cmap = mc.ListedColormap(n.vstack((cmap_bot,cmap_top)))


		## data
		dt = dt_dic['z_ws']
		# dt.replace(0.,n.nan,inplace=True)

		## plot
		## set z_ws as background and the colorbar is horizontal
		pm = ax.pcolormesh(dt.index,dt.keys(),dt[1:].T[1:],cmap=cmap,vmin=setting['vmin'],vmax=setting['vmax'])

		box = ax.get_position()
		cax = fig.add_axes([box.x0,.045,box.width,.015])
		
		cb = fig.colorbar(pm,cax=cax,extend='both',orientation='horizontal')

		cb.ax.tick_params(which='major',length=5.,labelsize=fs-2.)
		cb.ax.tick_params(which='minor',length=2.5)
	
		cb.ax.set_title(setting['cb_label'],fontsize=fs-2.)

	def _plot(meta_nam):
		## plot quiver and plot z_ws
		meta = meta_dt[meta_nam]

		## parameter
		fs = 15.
		setting = meta['quiver']

		## plot
		fig, ax = subplots(figsize=(12,8),dpi=150.)

		box = ax.get_position()
		ax.set_position([box.x0,box.y0+0.05,box.width,box.height])

		## z_ws
		if 'z_ws' in dt_dic.keys(): _plot_z_ws(fig,ax,fs,ax.get_position(),meta)
		## quiver
		x_tick, _st, _fn = _plot_quiver(fig,ax,fs,ax.get_position(),meta)

		## other figure setting
		ax.tick_params(which='major',length=6.,labelsize=fs-2.)
		ax.tick_params(which='minor',length=3.5)

		ax.set(xticks=x_tick,ylim=(setting['ylim_bot'],setting['ylim_top']))
		ax.set_xticklabels(x_tick.strftime('%Y-%m-%d%n%HLST'))
		
		# ax.set_xlabel('Time',fontsize=fs)
		ax.set_ylabel('Height (m)',fontsize=fs)
		
		fig.suptitle(f'{dt_nam.upper()} lidar wind profile (every {setting["dt_freq"].replace("T"," min")}) ',fontsize=fs+2.,style='italic')

		fig.savefig(pth(save_path[meta_nam],f'{dt_nam}_wswd_{_st.strftime("%Y%m%d%H%M")}-{_fn.strftime("%Y%m%d%H%M")}.png'))


	## plot
	# _plot_pcolor('ws','jet')
	# _plot_pcolor('z_ws',cmap)

	# _plot('comp')
	_plot(dt_nam)

