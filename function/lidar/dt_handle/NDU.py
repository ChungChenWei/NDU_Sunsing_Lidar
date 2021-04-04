
# sub class
## lidar NDU
## National Defense University
## extension : .csv
## height 	 : 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
## frequence : 1s
## variable  : u, v, w, ws, wd ; 
##			   temp, RH, pressure, Az



from lidar.dt_handle import lidar_reader, dtm, pth
from pandas import read_csv


class reader(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='NDU',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:

			try:
				## lidar calibrate for 1 min after start the lidar
				_df = read_csv(f,skiprows=1,parse_dates=['Time'],na_values=[99.9,999.9],
							   date_parser=lambda _: dtm.strptime(_,'%Y%m%d_%X.%f')).set_index('Time').resample('1s').mean()

				if _file[-8::-4] != '0000': _df.drop(_df.index[0:60],inplace=True)
				_flist.append(_df)	
			except:
				## if wrong file appear
				return _flist
				
		return _flist