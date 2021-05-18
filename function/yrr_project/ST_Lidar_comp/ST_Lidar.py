# main 
# version : 

# new		: 
# structure : 
# target	: 
# 1. 
import sys
from os.path import join as pth
sys.path.insert(1,pth('..','..'))

from datetime import datetime as dtm
from datetime import timedelta as dtmdt

from lidar.dt_handle import *
from lidar.plot import plot

import numpy as n

from pandas import read_csv, date_range, DataFrame, concat, Series
from radio.reader import *

from matplotlib.pyplot import subplots, close, show


import pickle as pkl
# from ground import *




"""


"""


## time decorater
def __timer(func):
	def __wrap():
		print(f'\nPROGRAM : {__file__}\n')
		__st = dtm.now().timestamp()

		## main function
		_out = func()

		__fn = dtm.now().timestamp()
		__run = (__fn-__st)/60.

		print(f'\nProgram done\nrunning time = {int(__run):3d} min {(__run-int(__run))*60.:6.3f} s')
		return _out

	return __wrap





## (1) linear interpolate lidar data
# '''
start_dtm = dtm(2021,4,1,0,0,0)
final_dtm = dtm(2021,4,6,0,0,0)
path = pth('..','..','..','data','Lidar_NDU','use')
reader = NDU.reader(path,start_dtm,final_dtm)
dt = reader.get_data()


dt_u, dt_v = -n.sin(dt['wd']/180.*n.pi)*dt['ws'], -n.cos(dt['wd']/180.*n.pi)*dt['ws']


def height_inter(_df,inter_h):

	key_lst = list(_df.keys())
	inter_lst = n.arange(key_lst[0],key_lst[-1]+inter_h,inter_h).tolist()

	add_lst = inter_lst.copy()
	[ add_lst.remove(_) for _ in key_lst ]

	for _ in add_lst: _df[_] = n.nan

	return _df[inter_lst].interpolate(axis=1)

def uv2wswd(u,v):
	return n.sqrt((u**2)+(v**2)), (n.arctan2(-u,-v)*180./n.pi)%360.

ws_inte, wd_inte = uv2wswd(height_inter(dt_u,50),height_inter(dt_v,50))

## plot 
plot.plot_all({'nam':'inteNDU','ws':ws_inte,'wd':wd_inte,'z_ws':dt['z_ws']},pth('picture'),tick_freq='24h')

# '''


## (2) get ST at wanted time, plot height-time
from pathlib import Path

DATA_ROOT = Path('..') /Path('..') /Path('..') / "data"
ST_DATA   = DATA_ROOT  / "storm tracker"
METADATA  = Path('..') /Path('..') /Path('.')  / "radio"

def readSTLaunchMetaData():
	ST_RootPath = Path('..') /Path('..') /Path('..') / "data" / "storm tracker"
	ST_launchMetaDataFileName = "20210401_20210406.csv"
	ST_rename = {"NO.":"no", "Time (yyyy/mm/dd HH:MM:SS)":"time"}

	ST_launchMetaData = read_csv(ST_RootPath / ST_launchMetaDataFileName, parse_dates=['Time (yyyy/mm/dd HH:MM:SS)']).dropna(subset=['Time (yyyy/mm/dd HH:MM:SS)']).reset_index(drop=True)
	ST_launchMetaData = ST_launchMetaData[['NO.','Time (yyyy/mm/dd HH:MM:SS)']].rename(columns=ST_rename).astype({'no': 'int32'})

	return ST_launchMetaData

md = readSTLaunchMetaData()
cmap_no = n.linspace(0.,2.,md.size)


## ## plot ST [25, 26, 27] completed vertical profile
'''

fs = 13.


fig, ax = subplots(figsize=(8,6),dpi=150.)
# fig, ax = subplots()

first_tm = None
for _no in md.no.iloc[[30,31,32]]:

	print(f'\n\nno.{_no}\n')

	stObj = STreader(_no,L0DataPath=Path(ST_DATA / 'Level 0'),metaPath=METADATA)

	_df = stObj.L0Reader()[0][['Z [m]','U [m/s]','V [m/s]']]
	first_tm = first_tm if first_tm is not None else _df.index[0]

	_df = _df[~_df.index.duplicated(keep='first').copy()]
	_df = _df.reindex(_df.index.sort_values()).where(_df['Z [m]']>=150.)

	# try:
		# last_indx = _df.where(_df['Z [m]']>=1100.).dropna(subset=['Z [m]']).index[0]
	# except:
		# last_indx = _df['Z [m]'].idxmax()

	# _df = _df.loc[_df.index[0]:last_indx]
	# x_tick = date_range(_df.index[0].strftime('%Y-%m-%d'),_df.index[-1].strftime('%Y-%m-%d'),freq='3h')


	# ax.plot(_df['Z [m]'],c='#4c79ff',marker='o',mfc='None',ms=4)
	ax.plot(_df['Z [m]'],c='#26c9ff',marker='o',mfc='None',ms=4)

# final_tm = _df.index[-1]

x_tick = date_range('2021-04-02 21:00:00','2021-04-03 03:00:00',freq='3h')

ax.tick_params(which='major',direction='in',length=7,labelsize=fs-2.5)
ax.tick_params(which='minor',direction='in',length=4.5)

# [ ax.spines[axis].set_visible(False) for axis in ['right','top'] ]
ax.set(xlim=(x_tick[0],x_tick[-1]))

ax.set_xlabel('Time',fontsize=fs)
ax.set_ylabel('Height (m)',fontsize=fs)

ax.set_xticks(x_tick)
ax.set_xticklabels(x_tick.strftime('%Y-%m-%d %HLST'))

# ax.legend(framealpha=0,fontsize=fs-2.)
#ax.legend(handles=[],framealpha=0,fontsize=fs-2.)

# ax.set_title('',fontsize=fs)	
fig.suptitle('ST below 1100 km',fontsize=fs+2.,style='italic')	
fig.savefig(pth('picture',f'ST_height.png'))

# show()
close()
#'''

## plot ST and u v
'''
res = 0
if res:

	df_all_u = []
	df_all_v = []
	first_tm = None
	for _no, colr in zip(md.no,cmap_no):

		print(f'\n\nno.{_no}\n')

		stObj = STreader(_no,L0DataPath=Path(ST_DATA / 'Level 0'),metaPath=METADATA)

		_df = stObj.L0Reader()[0][['Z [m]','U [m/s]','V [m/s]']]
		first_tm = first_tm if first_tm is not None else _df.index[0]

		_df = _df[~_df.index.duplicated(keep='first').copy()]
		_df = _df.reindex(_df.index.sort_values())[_df['Z [m]']>=150.]

		try:
			last_indx = _df.where(_df['Z [m]']>=1100.).dropna(subset=['Z [m]']).index[0]
		except:
			last_indx = _df['Z [m]'].idxmax()

		_df = _df.loc[_df.index[0]:last_indx]

		## process data
		_df['hh'] = _df.index.map(lambda _: dtm.strftime(_,'%h'))
		_df = _df.where(_df['hh']==_df['hh'][-1])

		u_dic = {}
		v_dic = {}
		for top, bot in zip(n.arange(200,1050,50),n.arange(150,1000,50)):
			u_dic[top] = _df.where((_df['Z [m]']>bot)&(_df['Z [m]']<top))['U [m/s]'].mean()
			v_dic[top] = _df.where((_df['Z [m]']>bot)&(_df['Z [m]']<top))['V [m/s]'].mean()


		df_all_u.append(Series(u_dic))
		df_all_v.append(Series(v_dic))


		# if df_all_v.__len__() ==20: break
		
		## plot
		# ax.quiver(_df.index,_df.keys(),)

	## get u, v dataframe
	u_df = concat(df_all_u,axis=1).T.set_index(date_range(first_tm.strftime('%Y-%m-%d %H:00:00'),periods=df_all_u.__len__(),freq='1h'))
	v_df = concat(df_all_v,axis=1).T.set_index(date_range(first_tm.strftime('%Y-%m-%d %H:00:00'),periods=df_all_u.__len__(),freq='1h'))




	## save
	with open(pth('u_ST.pkl'),'wb') as f:
		pkl.dump(u_df,f,protocol=pkl.HIGHEST_PROTOCOL)

	with open(pth('v_ST.pkl'),'wb') as f:
		pkl.dump(v_df,f,protocol=pkl.HIGHEST_PROTOCOL)

## load
if not res:
	print('read pickle')

	with open(pth('u_ST.pkl'),'rb') as f:
		u_df = pkl.load(f)
	with open(pth('v_ST.pkl'),'rb') as f:
		v_df = pkl.load(f)
# breakpoint()



x_tick = date_range('2021-04-01 00:00:00','2021-04-06 00:00:00',freq='24h')

## process u, v data

def uv2wswd(u,v):
	return n.sqrt((u**2)+(v**2)), (n.arctan2(-u,-v)*180./n.pi)%360.
def wswd2uv(_ws,_wd):
	return -n.sin(_wd/180.*n.pi)*_ws, -n.cos(_wd/180.*n.pi)*_ws

ws_ST, wd_ST = uv2wswd(u_df,v_df)


plot.plot_all({'nam':'ST','ws':ws_ST,'wd':wd_ST},pth('picture'),tick_freq='24h',input_tick=x_tick)

# '''


## plot ST horizontal distance
'''
from metpy.calc import lat_lon_grid_deltas as dist_calc

limit_h = 1100
limit_h = 500
limit_h = 200

res = 0
if res:

	dist = []

	for _no in md.no:

		print(f'\n\nno.{_no}\n')

		stObj = STreader(_no,L0DataPath=Path(ST_DATA / 'Level 0'),metaPath=METADATA)

		_df = stObj.L0Reader()[0][['Z [m]','Lat [o]','Lon [o]']]
		# first_tm = first_tm if first_tm is not None else _df.index[0]

		_df = _df[~_df.index.duplicated(keep='first').copy()]
		_df = _df.reindex(_df.index.sort_values())

		try:
			last_indx = _df.where(_df['Z [m]']>=limit_h).dropna(subset=['Z [m]']).index[0]
		except:
			last_indx = _df['Z [m]'].idxmax()

		_df = _df.loc[_df.index[0]:last_indx][['Lat [o]','Lon [o]']].iloc[[0,-1]]
		
		dx, dy = dist_calc(_df['Lon [o]'],_df['Lat [o]'])
		dist.append(((dx[0]**2+dy[0,0]**2)**.5).m[0])

	dist = n.array(dist)
	## save
	with open(pth(f'ST_dist_{limit_h}.pkl'),'wb') as f:
		pkl.dump(dist,f,protocol=pkl.HIGHEST_PROTOCOL)

## load
if not res:
	print('read pickle')

	with open(pth(f'ST_dist_{limit_h}.pkl'),'rb') as f:
		dist = pkl.load(f)

## parameter
fs = 13.


## plot
fig, ax = subplots(figsize=(8,6),dpi=150.)

ax.plot(dist,range(dist.size),c='#000000',marker='^',ms=8,ls='',mfc='None')

ax.tick_params(which='major',direction='in',length=7,labelsize=fs-2.5)
ax.tick_params(which='minor',direction='in',length=4.5)
[ ax.spines[axis].set_visible(False) for axis in ['right','top'] ]
ax.set(xlim=(0.,2200.))

ax.set_xlabel('Horizontal Distance (m)',fontsize=fs)
ax.set_ylabel('ST',fontsize=fs)

# ax.set_title('',fontsize=fs)	
fig.suptitle(f'Horizontal Distance of each ST below {limit_h} m(height)',fontsize=fs+2.,style='italic')	
fig.savefig(pth('picture',f'ST_hor_dist_{limit_h}.png'))
# show()
close()

# '''



## plot ST horizontal distance (multiple)
'''
print('read pickle')

dist = {}
for _h in [1100,500,200]:
	
	with open(pth(f'ST_dist_{_h}.pkl'),'rb') as f:
		dist[_h] = pkl.load(f)

## parameter
fs = 14.

# breakpoint()
## plot
fig, ax = subplots(figsize=(8,9),dpi=150.)

for _x, _y in zip(DataFrame(dist).values,n.arange(97)):
	ax.plot(_x,[_y]*3,c='#777777',ls='--',lw=.4)

handle = []
for (_key, _val), colr, mk in zip(dist.items(),['#ff4c79','#26c9ff','#666666'],['o','*','^']):
	sc = ax.scatter(_val,range(_val.size),marker=mk,fc='None',ec=colr,label=f'below {_key} m',zorder=_key)
	handle.append(sc)



ax.tick_params(which='major',direction='in',length=7,labelsize=fs-2.5)
ax.tick_params(which='minor',direction='in',length=4.5)
[ ax.spines[axis].set_visible(False) for axis in ['right','top'] ]
ax.set(xlim=(0.,2200.))

ax.set_xlabel('Horizontal Distance (m)',fontsize=fs)
ax.set_ylabel('ST',fontsize=fs)

ax.legend(handles=handle,framealpha=0,fontsize=fs-2.)

# ax.set_title('',fontsize=fs)	
fig.suptitle(f'Horizontal Distance of each ST below 1100, 500, 200 m(height)',fontsize=fs+2.,style='italic')	
fig.savefig(pth('picture',f'ST_hor_dist_all.png'))
# show()
close()

# '''


'''

_mask = ws_ST.copy()<2.5
ws_ST.mask(_mask,n.nan,inplace=True)
ws_ST.replace(0.,n.nan,inplace=True)

_u, _v = wswd2uv(1.5,wd_ST)









		(1) replace 0 as nan, process the by-product after interpolate
		(2) get the mask below 2.5
		(3) set the value as nan under mask
		(4) get the mask out value, apply scatter plot
		
		
		
		_index, _height =n.meshgrid(dt_ws.index,dt_ws.keys())

		change ws, wd to u, v
		get height as y axis and get x ticks
		
		height = n.array(list(dt_ws.keys())).astype(float)
		x_tick = dt_ws.asfreq(tick_freq).index

		plot
		sc = ax.scatter(_index[_mask.T],_height[_mask.T],s=15,fc='None',ec='#666666',label='< 2.5 m/s')

		qv = ax.quiver(_u.index,height[::setting['sep']],_u.T[::setting['sep']],_v.T[::setting['sep']],dt_ws.T[::setting['sep']].values,
					   cmap=cmap,scale=50,clim=(setting['vmin'],setting['vmax']))









# '''



























## (3) 
## compair with lidar
## mean u v to 50m ?
















