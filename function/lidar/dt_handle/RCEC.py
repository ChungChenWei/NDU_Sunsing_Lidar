
# sub class
## lidar RCEC
## Research Center of Environmental Changes
## extension : .csv
## height 	 : 51, 77, 103, ... ,4988, 5014 (60m ~ 5820m * sin(60) ) 
## frequence : 5 min
## variable  : ws, wd, SNR, dtObtRate, std, ws_max, ws_max, z_ws, z_ws_std ; 
##			   temp, RH, pressure


from lidar.dt_handle import lidar_reader, dtm, pth
from pandas import read_csv


class reader(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='RCEC',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:

			_flist.append(read_csv(f,skiprows=1,parse_dates=['Date_time'],na_values=[99.9,999],
								   date_parser=lambda _: dtm.strptime(_,'%Y%m%d %X')).set_index('Date_time').resample('5T').mean())
		return _flist