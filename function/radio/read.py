import logging
from json import load
from pathlib import Path
from pandas import DataFrame
from pandas import read_csv
from datetime import datetime  as dtmdtm
from datetime import timedelta as dtmdt

import metpy.calc as mcalc
from metpy.plots import SkewT, Hodograph
from metpy.units import units

import matplotlib.pyplot   as plt
import matplotlib.gridspec as gs
import shapefile
from descartes import PolygonPatch


import numpy as np

with open('metadata.json') as js:
    meta = load(js)

shp = shapefile.Reader(r'D:\map\twcounty\twcounty')
rec = shp.records()
shapes = shp.shapes()

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

        return P_released * units.hPa, T_released * units.degreeC, TD_released * units.degreeC, U_released, V_released

    def plot(self, picPath=Path('.')):
        boundary = {"T":[-200, 40, 5], "P":[1100,100]}
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
        fs = 16

        ## Data input
        P,T,Td,U,V = self.read()
        profP      = P
        profT      = T
        profTd     = Td
        ## calc 
        LCL_P, LCL_T = mcalc.lcl(P[0], T[0], Td[0])
        # LFC_P, LFC_T = mcalc.lfc(P, T, Td)
        while(True):
            try:
                parcel_prof  = mcalc.parcel_profile(profP, T[0], Td[0]).to('degC')
                break
            except:
                profP  = profP[1:]
                profT  = profT[1:]
                profTd = profTd[1:]
            finally:
                if(len(profP)==0):
                    break

        ## fig setting
        grid = gs.GridSpec(3,3)
        fig  = plt.figure(figsize=(12, 12))
        fig.text(0.55,0.89,f"no_{self.no} {self.release_time} LST",fontsize=fs-6)

        # fig.subplots_adjust(top = 0.9, bottom = 0.1, left = 0.05, right = 0.96, wspace = 0.08, hspace = 0.25)

        skew = SkewT(fig, subplot=grid[:, :], rotation=45)
        
        ##special lines
        skew.ax.set_xticks(np.arange(boundary["T"][0], boundary["T"][1], boundary["T"][2]))
        skew.plot_dry_adiabats(**linestyle["dry_adiabats"])
        skew.plot_moist_adiabats(**linestyle["moist_adiabats"]) 
        skew.plot_mixing_lines(p=[1000,500]*units.hPa,**linestyle["mixing_lines"])
        
        ##title etc.,
        UTC = max((self.release_time + dtmdt(minutes=25)).hour, (self.release_time - dtmdt(minutes=25)).hour) - 8

        skew.ax.set_title(f"Skew-T Log-P Diagram Storm tracker {UTC} UTC\n")
        skew.ax.set_xlabel('[$\degree C$]', fontsize = fs)
        skew.ax.set_ylabel('[$hPa$]', fontsize = fs)
    
        skew.ax.set_xlim(-40, 40) 
        skew.ax.set_ylim(boundary["P"][0], boundary["P"][1])
        for i in np.arange(boundary["T"][0], boundary["T"][1], boundary["T"][2]*2):
            plt.fill_between(range(i, i+boundary["T"][2]+1), boundary["P"][0], boundary["P"][1], color = 'yellow', alpha=0.7)
        
        ## main data
        skew.plot(P, T,  'b')
        skew.plot(P, Td, 'r')
        ### wind bar
        # idx  = mcalc.resample_nn_1d(P.m, np.array([1000, 975, 950, 925, 900, 850, 800, 750, 700, 650, 600, 500]))
        # skew.plot_barbs(P[idx], U[idx], V[idx], plot_units = units('knots'), xloc=1.05)
        skip=35
        skew.plot_barbs(P[::skip], U[::skip], V[::skip], plot_units = units('m/s'), xloc=1.05)

        skew.plot(LCL_P, LCL_T, 'ko', markerfacecolor='black')
        skew.plot(profP, parcel_prof, 'k', linewidth=2)

        ## CAPE CIN
        cape, cin = mcalc.cape_cin(profP, profT, profTd, parcel_prof)
        skew.shade_cin(profP,  profT, parcel_prof, color='b', alpha=0.5)
        skew.shade_cape(profP, profT, parcel_prof, color='r', alpha=0.5)
        fig.text(0.55,0.89,f"no_{self.no} {self.release_time} LST",fontsize=fs-6)

        figx = 0.61
        figy = 0.85
        fig.text(figx, figy     , f'$CAPE$= {cape.m:.1f} $J/kg$', fontsize = fs-4)
        fig.text(figx, figy-0.02, f'$CIN$ = {cin.m:.1f} $J/kg$' , fontsize = fs-4)
        fig.text(figx, figy-0.04, f'$LCL$ = {LCL_P.m:.1f} $hPa$', fontsize = fs-4)
        # fig.text(figx, figy-0.06, f'$LFC$ = {LFC_P.m:.1f} $hPa$', fontsize = fs-4)


        # # Create a hodograph
        # ax1 = fig.add_subplot(grid[0, -1])
        # h   = Hodograph(ax1, component_range=60.)
        # h.add_grid(increment=20)
        # h.plot(U[::20], V[::20])
        # ax1.tick_params(labelsize = fs-4)
        # ax1.set_xticks(np.arange(-50., 75., 25.))
        # ax1.set_yticks(np.arange(-50., 75., 25.))
        # ax1.set_xticklabels([])
        # ax1.set_title('Hodograph', fontsize = fs)
        # ax1.set_xlabel('WS [$m/s$]', fontsize = fs-4)
        # ax1.set_ylabel('WS [$m/s$]', fontsize = fs-4)

        # ax2 = fig.add_subplot(grid[1, -1])
        # [ax2.add_patch(PolygonPatch(shape, fc= 'none')) for shape in shapes]
        # # ax2.scatter(lon[10:], lat[10:], c = 'r', s = 10)
        # ax2.tick_params(labelsize = 15.)
        # ax2.set_xticks(np.arange(119.5, 122., 0.5))
        # ax2.set_yticks(np.arange(22., 24.5, 0.5))
        # ax2.set_xticklabels(['', '120°E', '', '121°E', ''])
        # ax2.set_yticklabels(['22°N', '', '23°N', '', '24°N'])
        # ax2.set_xlim([119.5, 121.5])
        # ax2.set_ylim([22, 24])
        # ax2.grid(linestyle = '--')
        # ax2.set_title('Trajectory', fontsize = 20.)
        # ax2.set_xlabel('longitude',  fontsize = 15.)
        # ax2.set_ylabel('latitude', fontsize = 15.)


        plt.savefig(picPath / (f"{UTC}Z_{self.release_time.strftime('%Y%m%d_%H%M')}_no{self.no}.png"))
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
        
    mode = ""
    # mode = "DEBUG"
    if(mode!="DEBUG"):
        for no, time in launch.items():
            try:
                st = STreader(no, time, Path('../../data/ST'))
                st.plot(Path('../../picture/ST'))
            except:
                logger.warning(f"{no} fail", exc_info=True)
    else:
        st = STreader(2285, "2021/04/01 21:00:00", Path('../../data/ST'))
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
