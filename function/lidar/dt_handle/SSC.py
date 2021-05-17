
# sub class
## lidar SSC
## Smartec Scientific Corp
## extension : .xlsx
## height 	 : 38, 59, 79, 99, 119, 139, 159, 179, 199, 224, 249
## frequence : 10 min
## variable  : packet, wd, ws, ws_min, ws_max, ws_std, z, TI ; 
##			   bearing, tilt, temp, pressure, RH, ws_ground, wd_ground, rain, fog


from lidar.dt_handle import lidar_reader, dtm, pth
from pandas import read_csv
from numpy import arange
from datetime import timedelta as dtmdt


class reader(lidar_reader):

	nam = 'SSC'

	def _lidar_reader__raw_reader(self,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:

			_temp = read_csv(f,skiprows=1)

			_tm_list = []
			for _ in _temp['Time and Date']:
				
				if '\u4e0a\u5348' in _:
					_tm_list.append(dtm.strptime(_.replace('\u4e0a\u5348','AM'),'%Y/%m/%d %p %X'))
				elif '\u4e0b\u5348' in _:
					_tm_list.append(dtm.strptime(_.replace('\u4e0b\u5348','PM'),'%Y/%m/%d %p %X')+dtmdt(hours=12))
				else:
					_tm_list = _temp['Time and Date'].apply(lambda _: dtm.strptime(_,'%d/%m/%Y %X')).copy()
					break

			_temp['Time'] = _tm_list

		return _temp.set_index('Time').resample('10T').mean()





