import logging
from json import load
from pathlib import Path
from pandas import DataFrame
from pandas import read_csv, read_table
from datetime import datetime  as dtmdtm
from datetime import timedelta as dtmdt

import metpy.calc as mcalc
from metpy.plots import SkewT, Hodograph
from metpy.units import units

import matplotlib.pyplot   as plt
import matplotlib.gridspec as gs
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import shapefile
from descartes import PolygonPatch

import numpy as np

from multiprocessing import Pool

shp = shapefile.Reader(r'D:\map\twcounty\twcounty')
rec = shp.records()
shapes = shp.shapes()

def metadataReader(filePath):
    with open(filePath) as js:
        return load(js)

class sounding:
    def __init__(self, path=Path('.'), metaFilePath=Path('.')):
        self.path = path
        self.meta = metadataReader(metaFilePath)
        self.plotMeta = self.meta["skewT"]

    def reader(self, sounding, wdShift=0):
        if(type(sounding)==None):
            logger.error("sounding data empty")
            return

        ## basic variables
        P_released    = sounding[self.soundingMeta["P"]][:].to_numpy(dtype=float)
        T_released    = sounding[self.soundingMeta["T"]["name"]][:].to_numpy(dtype=float)
        Z_released    = sounding[self.soundingMeta["Z"]][:].to_numpy(dtype=float)
        RH_released   = sounding[self.soundingMeta["RH"]][:].to_numpy(dtype=float)
        WS_released   = sounding[self.soundingMeta["WS"]["name"]][:].to_numpy(dtype=float)
        WD_released   = ((sounding[self.soundingMeta["WD"]][:] - wdShift)%360).to_numpy(dtype=float)
        ## metpy cal
        TD_released   = mcalc.dewpoint_from_relative_humidity(T_released * units(f'{self.soundingMeta["T"]["unit"]}'), RH_released/100).m
        U_released, V_released = mcalc.wind_components(WS_released * units(f'{self.soundingMeta["WS"]["unit"]}'), WD_released * units.degrees)

        return P_released * units.hPa, T_released * units.degreeC, TD_released * units.degreeC, U_released, V_released

    def plotter(self, skew):
        boundary  = self.plotMeta["boundary"]
        linestyle = self.plotMeta["linestyle"]
        linestyle["dry_adiabats"]["t0"] = np.arange(-100, 300, 10) * units.celsius
        self.fs   = 16
        ## basic vars
        P, T, Td, U, V = self.read()
        ## LCL
        LCL_parcel_idx = 0
        LCL_P, LCL_T = mcalc.lcl(P[LCL_parcel_idx], T[LCL_parcel_idx], Td[LCL_parcel_idx])

        ## shift profile
        profP      = P
        profT      = T
        profTd     = Td
        ## calc 
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

        ##special lines
        skew.ax.set_xticks(np.arange(boundary["T"][0], boundary["T"][1], boundary["T"][2]))
        skew.plot_dry_adiabats(**linestyle["dry_adiabats"])
        skew.plot_moist_adiabats(**linestyle["moist_adiabats"]) 
        skew.plot_mixing_lines(p=[1000,500]*units.hPa,**linestyle["mixing_lines"])
        
        skew.ax.set_xlabel('[$\degree C$]', fontsize = self.fs)
        skew.ax.set_ylabel('[$hPa$]',       fontsize = self.fs)

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
        skip=self.plotMeta["wind"]["skip"]
        skew.plot_barbs(P[P.m>=100][::skip], U[P.m>=100][::skip], V[P.m>=100][::skip], plot_units = units('m/s'), xloc=1.05)

        skew.plot(LCL_P, LCL_T, 'ko', markerfacecolor='black')
        skew.plot(profP, parcel_prof, 'k', linewidth=2)


        # ## CAPE CIN
        # cape, cin = mcalc.cape_cin(profP, profT, profTd, parcel_prof)
        # skew.shade_cin(profP,  profT, parcel_prof, color='b', alpha=0.5)
        # skew.shade_cape(profP, profT, parcel_prof, color='r', alpha=0.5)
        # fig.text(0.55,0.89,f"no_{self.no} {self.release_time} LST",fontsize=fs-6)

        # figx = 0.61
        # figy = 0.85
        # fig.text(figx, figy     , f'$CAPE$= {cape.m:.1f} $J/kg$', fontsize = fs-4)
        # fig.text(figx, figy-0.02, f'$CIN$ = {cin.m:.1f} $J/kg$' , fontsize = fs-4)
        # fig.text(figx, figy-0.04, f'$LCL$ = {LCL_P.m:.1f} $hPa$', fontsize = fs-4)
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

class RS41reader(sounding):
    def __init__(self, release_time, path=Path('.'), metaPath=Path('.')):
        super().__init__(path=path,  metaFilePath=metaPath / 'metadata.json')
        self.release_time = dtmdtm.strptime(release_time,"%Y%m%d_%H%M")
        self.soundingMeta = self.meta["radio"]["RS41"]

    def read(self):
        no_file   = self.path / f"edt2_{self.release_time.strftime('%Y%m%d_%H%M')}.txt"
        logger.info(f"Start reading RS41 {self.release_time}")

        with open(no_file) as rs_file:
            sounding = read_table(rs_file,skiprows=[0,1,2,3,5],delimiter='\s+')
        
        return self.reader(sounding)

    def plot(self, picPath=Path('.'), showmode=False):
        ## fig setting
        grid = gs.GridSpec(3,3)
        fig  = plt.figure(figsize=(12, 12))

        # fig.subplots_adjust(top = 0.9, bottom = 0.1, left = 0.05, right = 0.96, wspace = 0.08, hspace = 0.25)
        # skew = SkewT(fig, subplot=grid[:, :], rotation=45)
        skew = SkewT(fig, rotation=45)
        
        self.plotter(skew)

        ## UTC
        UTC = self.release_time.hour

        fig.text(0.55,0.89,f"{self.release_time+dtmdt(hours=8)} LST",fontsize=self.fs-6)
        skew.ax.set_title(f"Skew-T Log-P Diagram RS41 {UTC:02d} UTC\n", fontsize=self.fs)
    
        plt.savefig(picPath / (f"{self.release_time.strftime('%Y%m%d')}_{UTC:02d}Z_{(self.release_time+dtmdt(hours=8)).strftime('%Y%m%d_%H%M')}.png"))
        if(showmode == True):
            plt.show()

## 2305 05 59 50
class STreader(sounding):
    def __init__(self, no, release_time, path=Path('.'), metaPath=Path('.')):
        super().__init__(path=path, metaFilePath=metaPath / 'metadata.json')
        self.no   = no
        self.release_time = dtmdtm.strptime(release_time,"%Y/%m/%d %H:%M:%S") 
        self.soundingMeta = self.meta["radio"]["ST"]

    def read(self):
        no_file   = self.path / f"no_{self.no}.csv"
        logger.info(f"Start reading ST no_{self.no}")

        with open(no_file) as st_file:
            sounding = read_csv(st_file,parse_dates=[0])
        ## timer read
        time          = sounding['Time'][:]
        self.sounding = sounding.loc[sounding[self.soundingMeta["Time"]] >= self.release_time]

        return self.reader(self.sounding, wdShift=180)

    def plot(self, picPath=Path('.'), showmode=False, savemode=True):
        ## fig setting
        grid = gs.GridSpec(3,3)
        fig  = plt.figure(figsize=(12, 12))
        # fig.subplots_adjust(top = 0.9, bottom = 0.1, left = 0.05, right = 0.96, wspace = 0.08, hspace = 0.25)
        # skew = SkewT(fig, subplot=grid[:, :2], rotation=45)
        skew = SkewT(fig, rotation=45)
        
        self.plotter(skew)

        ## UTC
        UTC = max((self.release_time + dtmdt(minutes=25)).hour, (self.release_time - dtmdt(minutes=25)).hour) - 8
        if(UTC < 0):
            UTC += 24
            title = (self.release_time - dtmdt(days=1)).strftime('%Y%m%d')
        else:
            title = self.release_time.strftime('%Y%m%d')

        fig.text(0.55,0.89,f"no_{self.no} {self.release_time} LST",fontsize=self.fs-6)
        skew.ax.set_title(f"Skew-T Log-P Diagram Storm tracker {title} {UTC:02d} UTC\n")
        if(savemode == True):
            plt.savefig(picPath / (f"{title}_{UTC:02d}Z_{self.release_time.strftime('%Y%m%d_%H%M')}_no{self.no}.png"))
        if(showmode == True):
            plt.show()


        # ax2 = fig.add_subplot(grid[0, 2])
        # [ax2.add_patch(PolygonPatch(shape, fc= 'none')) for shape in shapes]
        # ax2.scatter(self.sounding['Lon'][10:], self.sounding['Lat'][10:], c = 'r', s = 10)
        # ax2.tick_params(labelsize = 15.)
        # lonl = 120.
        # lonr = 121.
        # latl = 23.
        # latr = 23.5
        # ax2.set_xticks(np.arange(lonl, lonr, 0.5))
        # ax2.set_yticks(np.arange(latl, latr, 0.5))
        # # ax2.set_xticklabels(['', '120°E', '', '121°E', ''])
        # # ax2.set_yticklabels(['22°N', '', '23°N', '', '24°N'])
        # ax2.set_xlim([lonl, lonr])
        # ax2.set_ylim([latl, latr])
        # ax2.grid(linestyle = '--')
        # ax2.set_title('Trajectory', fontsize = self.fs)
        # ax2.set_xlabel('longitude',  fontsize = self.fs-4)
        # ax2.set_ylabel('latitude', fontsize = self.fs-4)

        # plt.savefig(picPath / (f"{title}_{UTC}Z_{self.release_time.strftime('%Y%m%d_%H%M')}_no{self.no}_tj.png"))
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
    with open('RSlaunchdata.json') as js:
        RSlaunch = load(js)["launch"]
        
    # mode = "DEBUG"
    mode = "STMUL"
    if(mode=="DEBUG"):
        stID = 401
        st = STreader(stID, launch[f"{stID}"], Path('../../data/ST'))
        st.plot(Path('../../picture/ST'), showmode=True, savemode=False)
        # rs = RS41reader('20210401_1500',Path('../../data/RS41/202104_TNNUA_NTU'))
        # rs.plot(Path('../../picture/RS41'))
    elif(mode=="STMUL"):
        fig  = plt.figure(figsize=(12, 12),constrained_layout=True)
        # skew = SkewT(fig, rotation=0, aspect=100)

        linestyle = metadataReader('metadata.json')['skewT']["linestyle"]
        boundary  = metadataReader('metadata.json')['skewT']["boundary"]
        fs = 16
        
        # skew.ax.set_xlabel('[$\degree C$]', fontsize = fs)
        # skew.ax.set_ylabel('[$hPa$]',       fontsize = fs)

        # for i in np.arange(boundary["T"][0], boundary["T"][1], boundary["T"][2]*2):
        #     plt.fill_between(range(i, i+boundary["T"][2]+1), boundary["P"][0], boundary["P"][1], color = 'yellow', alpha=0.7)
        
        ### wind bar
        # idx  = mcalc.resample_nn_1d(P.m, np.array([1000, 975, 950, 925, 900, 850, 800, 750, 700, 650, 600, 500]))
        # skew.plot_barbs(P[idx], U[idx], V[idx], plot_units = units('knots'), xloc=1.05)
        # skip=self.plotMeta["wind"]["skip"]
        # skew.plot_barbs(P[P.m>=100][::skip], U[P.m>=100][::skip], V[P.m>=100][::skip], plot_units = units('m/s'), xloc=1.05)

        # skew.plot(LCL_P, LCL_T, 'ko', markerfacecolor='black')
        # skew.plot(profP, parcel_prof, 'k', linewidth=2)

        # noL  = list(launch.keys())[-8:]
        noL    = list(launch.keys())[-12:]
        # colorL = ['r','o','y','g','b','p','k','']
        cmap   = cm.get_cmap('rainbow', 10)
        colorL = cmap(range(10))
        i      = 0
        for no in noL:
            time = dtmdtm.strptime(launch[f"{no}"],"%Y/%m/%d %H:%M:%S")
            print(no, time) 
            st = STreader(no, launch[f"{no}"], Path('../../data/ST'))
            try:

                P, T, Td, U, V = st.read()
                Theta   = mcalc.potential_temperature(P,T).to('K')
                print(Theta)
                Thetae  = mcalc.equivalent_potential_temperature(P,T,Td).to('K')

                ## UTC
                UTC = max((time + dtmdt(minutes=25)).hour, (time - dtmdt(minutes=25)).hour) - 8
                LST = max((time + dtmdt(minutes=25)).hour, (time - dtmdt(minutes=25)).hour)
                if(UTC < 0):
                    UTC += 24
                    title = (time - dtmdt(days=1)).strftime('%m%d')
                else:
                    title = time.strftime('%m%d')


                ## main data
                plt.plot(Thetae, P,color=colorL[i] , linewidth=2, label=f"{title} {UTC:02d}Z ({LST:02d} LST)")
                i += 1
                # skew.plot(P, Td, 'r')

            except:
                print('err')
        plt.ylim(1000, 500)
        plt.xlim(300,  400)
        plt.title("Thetae", fontsize=20)
        plt.xlabel('K')
        plt.ylabel('hPa')
        plt.legend()
        plt.grid()
        plt.savefig("STMUL_Thetae.png")
        plt.show()

                       
    else:
        if(mode == "ST"):
            for no, time in launch.items():
                try:
                    st = STreader(no, time, Path('../../data/ST'))
                    st.plot(Path('../../picture/ST'))
                except:
                    logger.warning(f"{no} fail", exc_info=True)
        if(mode == "RS"):
            for time in RSlaunch:
                try:
                    rs = RS41reader(time,Path('../../data/RS41/202104_TNNUA_NTU'))
                    rs.plot(Path('../../picture/RS41'))
                except:
                    logger.warning(f"{time} fail", exc_info=True)
       
