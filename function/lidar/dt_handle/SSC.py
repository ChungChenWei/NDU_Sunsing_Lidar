
# sub class
## lidar SSC
## Smartec Scientific Corp
## extension : .xlsx
## height 	 : 40, 45, 50, 55, 60, 65, 70, 75, 80, 100, 120, 140
## frequence : 1 min
## variable  : ws, ws_disp, wd, ws_max, z_ws, z_ws_disp, z_ws_std, cnr, cnr_min, Dopp Spect Broad, dt_ava ; 
##			   None



from lidar.dt_handle import lidar_reader, dtm, pth
from pandas import read_excel


class reader(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='SSC',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'rb') as f:
			_flist.append(read_excel(f,parse_dates=['Timestamp (end of interval)']
									 ).set_index('Timestamp (end of interval)').resample('1T').mean())
		return _flist