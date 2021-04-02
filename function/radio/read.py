import logging
from json import load
from pathlib import Path
from pandas import DataFrame
from pandas import read_csv
from datetime import datetime  as dtmdtm
from datetime import timedelta as dtmdt

import metpy.calc as mcalc
from metpy.plots import SkewT
from metpy.units import units

import matplotlib.pyplot as plt
import numpy as np

with open('metadata.json') as js:
    meta = load(js)


class RS41reader:
    pass


## 2305 05 59 50

class STreader:
    # import logging
    # __logger = logging.getLogger('__main__')
    def __init__(self, no, release_time, path=Path('.')):
        self.no   = no
        self.release_time = dtmdtm.strptime(release_time,"%Y/%m/%d %H:%M:%S") 
        self.path = path
        self.meta = meta["radio"]["ST"]
    def read(self):
        no_file   = self.path / f"no_{self.no}.csv"
        logger.info(f"Start reading ST no_{self.no}")

        with open(no_file) as st_file:
            sounding = read_csv(st_file,parse_dates=[0])
        ## timer read
        time          = sounding['Time'][:]
        ## release time mask
        time_mask     = time - self.release_time >= dtmdt(seconds=0)
        ## sensor data
        time_released = sounding[self.meta["Time"]][time_mask].to_numpy(dtype=float)
        P_released    = sounding[self.meta["P"]][time_mask].to_numpy(dtype=float)
        T_released    = sounding[self.meta["T"]][time_mask].to_numpy(dtype=float)
        Z_released    = sounding[self.meta["Z"]][time_mask].to_numpy(dtype=float)
        RH_released   = sounding[self.meta["RH"]][time_mask].to_numpy(dtype=float)
        WS_released   = sounding[self.meta["WS"]][time_mask].to_numpy(dtype=float)
        WD_released   = ((sounding[self.meta["WD"]][time_mask] - 180)%360).to_numpy(dtype=float)
        ## metpy cal
        TD_released   = mcalc.dewpoint_from_relative_humidity(T_released * units.degC, RH_released/100).m
        U_released, V_released = mcalc.wind_components(WS_released * units.km/units.hr, WD_released * units.degrees)

        return P_released, T_released, TD_released, U_released, V_released

    def plot(self, picPath=Path('.')):

        boundary = {"T":[-100, 40, 5], "P":[1100,100]}

        linestyle = {
            "dry_adiabats":{
                "t0"        : np.arange(-100, 300, 10) * units.celsius,
                "color"     : "blue",
                "alpha"     : 0.5,
                "linestyle" : "solid"
                },
            "moist_adiabats":{
                "color"     : "green",
                "alpha"     : 0.5,
                "linestyle" : "solid"
                },
            "mixing_lines":{
                "color"     : "black",
                "alpha"     : 0.4,
                "linestyle" : "dashed"
                }
        }


        P,T,Td,U,V = self.read()
        ##need the metpy package
        ##from metpy.plots import SkewT
        ##from metpy.units import units
        ##import metpy.calc as mcalc
        fig  = plt.figure(figsize=(8, 11.5))
        skew = SkewT(fig)
        skew.plot(P, T,  'b')
        skew.plot(P, Td, 'r')
        idx  = mcalc.resample_nn_1d(P, np.array([1000, 975, 950, 925, 900, 850, 800, 750, 700, 650, 600, 500]))
        skew.plot_barbs(P[idx], U[idx], V[idx], plot_units = units('m/s'))
        # skew.plot_barbs(P, U, V, plot_units = units('m/s'))
        
        ##special lines
        skew.ax.set_xticks(np.arange(boundary["T"][0], boundary["T"][1], boundary["T"][2]))
        skew.plot_dry_adiabats(**linestyle["dry_adiabats"])
        skew.plot_moist_adiabats(**linestyle["moist_adiabats"]) 
        skew.plot_mixing_lines(p=[1000,500]*units.hPa,**linestyle["mixing_lines"])
        ##title etc.,
        plt.title(f"no_{self.no} {self.release_time} LST")
        plt.xlim(-40, 40) 
        plt.ylim(boundary["P"][0], boundary["P"][1])
        for i in np.arange(boundary["T"][0], boundary["T"][1], boundary["T"][2]*2):
            plt.fill_between(range(i, i+boundary["T"][2]+1), boundary["P"][0], boundary["P"][1], color = 'yellow', alpha=0.7)
        
        plt.savefig(picPath / (f"{self.release_time.strftime('%Y%m%d_%H%M')}_no{self.no}.png"))
        # plt.show()

if __name__ == '__main__':
    import logging
    FORMAT = '%(asctime)s [%(levelname)s] %(module)s: %(message)s'
    DATEFORMAT = '%Y/%m/%d %H:%M:%S'
    logging.basicConfig(
        level = logging.INFO,
        format = FORMAT,
        datefmt = DATEFORMAT
        # handlers=[
        #     logging.FileHandler("debug.log"),
        #     logging.StreamHandler()
        # ]
    )
    logger = logging.getLogger('__main__')

    with open('launchdata.json') as js:
        launch = load(js)["launch"]
        
    for no, time in launch.items():
        st = STreader(no, time, Path('../../data/ST'))
        st.plot(Path('../../picture/ST'))

## radiosonde
'''

	def radiosonde_NTU(self,start,final):
		## read pickle or process raw data
		if ('radio_ntu.pkl' in listdir(self.path_radio_NTU))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of NTU radiosonde")
			with open(pth(self.path_radio_NTU,'radio_ntu.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of NTU radiosonde")

		## read raw data
		fList = []
		for file in listdir(self.path_radio_NTU):
			if '.txt' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_radio_NTU,file),'r',encoding='utf-8',errors='ignore') as f:
				fList.append(read_table(f,skiprows=[0,1,2,3,5],delimiter='\s+').set_index('HeightMSL'))
		print()
		
		fout = {}
		for time, _df in zip(self.index(start,final,'1d'),fList):
			fout[time.strftime('%Y/%m/%d')] = _df


		with open(pth(self.path_radio_NTU,'radio_ntu.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		## process different height
		# height = [40,45,50,55,60,65,70,75,80,100,120,140]
		# col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction (?','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   # 'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		# out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		# fout = {}
		# for col, nam in zip(col_nam,out_nam):
			# fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			# fout[nam].columns = height

		return fout

	def radiosonde_RCEC(self,start,final):
		## read pickle or process raw data
		if ('radio_rcec.pkl' in listdir(self.path_radio_RCEC))&(~self.reset):
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading pickle file of RCEC radiosonde")
			with open(pth(self.path_radio_RCEC,'radio_rcec.pkl'),'rb') as f:
				fout = pkl.load(f)
			return fout
		else: 
			print(f"\n\t{dtm.now().strftime('%m/%d %X')} : Reading file of RCEC radiosonde")

		## read raw data
		fList = []
		for file in listdir(self.path_radio_RCEC):
			if '.txt' not in file: continue
			print(f"\r\t\treading {file}",end='')

			with open(pth(self.path_radio_RCEC,file),'r',encoding='utf-8',errors='ignore') as f:
				fList.append(read_table(f,skiprows=2,delimiter=',\s+|\s+',engine='python').set_index('Height'))
		print()
		
		fout = {}
		for time, _df in zip(self.index(start,final,'1d'),fList):
			fout[time.strftime('%Y/%m/%d')] = _df

		with open(pth(self.path_radio_RCEC,'radio_rcec.pkl'),'wb') as f:
			pkl.dump(fout,f,protocol=pkl.HIGHEST_PROTOCOL)

		## process different height
		# height = [40,45,50,55,60,65,70,75,80,100,120,140]
		# col_nam = ['Wind Speed (m/s)','Wind Speed Dispersion (m/s)','Wind Direction (?','Z-wind Dispersion (m/s)','Z-wind (m/s)',
				   # 'Wind Speed min (m/s)','Wind Speed max (m/s)','CNR (dB)','CNR min (dB)','Dopp Spect Broad (m/s)','Data Availability (%)']
		# out_nam = ['ws','ws_disp','wd','ws_max','z_ws','z_ws_disp','z_ws_std','cnr','cnr_min','Dopp Spect Broad','dt_ava']

		# fout = {}
		# for col, nam in zip(col_nam,out_nam):
			# fout[nam] = _df[[ f'{_h}m {col}' for _h in height ]]
			# fout[nam].columns = height

		return fout




# start_dtm = dtm(2021,3,16,0,0,0)
# final_dtm = dtm(2021,3,16,0,0,0)
# dt = reader.radiosonde_RCEC(start_dtm,final_dtm)


# start_dtm = dtm(2021,3,16,0,0,0)
# final_dtm = dtm(2021,3,16,0,0,0)
# dt = reader.radiosonde_NTU(start_dtm,final_dtm)


# '''
