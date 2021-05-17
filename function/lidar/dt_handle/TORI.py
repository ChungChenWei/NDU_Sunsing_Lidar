
# sub class
## lidar TORI
## Taiwan Ocean Research Institute
## extension : .sta
## height 	 : 40, 45, 55, 65, 75, 85, 95, 115, 135, 155, 175, 195
## frequence : 1 min
## variable  : ws, ws_disp, wd, ws_max, z_ws, z_ws_disp, z_ws_std, cnr, cnr_min, Dopp Spect Broad, dt_ava ; 
##			   temp, ext temp, RH, pressure, Vbatt



from lidar.dt_handle import lidar_reader, dtm, pth
from pandas import read_table



class reader(lidar_reader):

	nam = 'TORI'

	def _lidar_reader__raw_reader(self,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:
			_df = read_table(f,skiprows=41,parse_dates=['Timestamp (end of interval)']
									 ).set_index('Timestamp (end of interval)').resample('1T').mean()
		return _df





