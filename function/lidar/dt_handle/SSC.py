
# sub class
## lidar SSC
## Smartec Scientific Corp
## extension : .xlsx
## height 	 : 38, 59, 79, 99, 119, 139, 159, 179, 199, 224, 249
## frequence : 10 min
## variable  : packet, wd, ws, ws_min, ws_max, ws_std, z, TI ; 
##			   None



from lidar.dt_handle import lidar_reader, dtm, pth
from pandas import read_csv


class reader(lidar_reader):
	def __init__(self,_path,_sta,_fin,reset=False):
		super().__init__(_path,_sta,_fin,_nam='SSC',_reset=reset)

	def _lidar_reader__raw_reader(self,_flist,_file):
		with open(pth(self.path,_file),'r',encoding='utf-8',errors='ignore') as f:



			## 先取出資料 然後 在進行分析判斷 在把資料塞回去 index  

			_flist.append(read_csv(f,skiprows=1).set_index('Time and Date').resample('10T').mean())

			

		return _flist





