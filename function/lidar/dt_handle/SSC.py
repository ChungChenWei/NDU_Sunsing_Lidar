
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


class reader(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='SSC',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:

			_temp = read_csv(f,skiprows=1)

			_tm_list = []
			for idx, _ in enumerate(_temp['Time and Date']):
				if '\u4e0a\u5348' in _:
					_tm_list.append(_.replace('\u4e0a\u5348','AM'))
				else:
					_tm_list.append(_.replace('\u4e0b\u5348','PM'))

			_temp['Time'] = _tm_list

			try:
				_time = _temp['Time'].apply(lambda _: dtm.strptime(_,'%Y/%m/%d %p %X')).copy()
			except:
				_time = _temp['Time'].apply(lambda _: dtm.strptime(_,'%d/%m/%Y %X')).copy()
			
			_flist.append(_temp.set_index(_time).resample('10T').mean())
			

		return _flist





