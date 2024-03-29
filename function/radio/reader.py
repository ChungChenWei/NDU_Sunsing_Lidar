from json    import load
from pathlib import Path
from pandas  import read_csv, read_table
from pandas  import DataFrame
from metpy.units  import units
from metpy.calc import dewpoint_from_relative_humidity, wind_components

from multiprocessing import Pool

import numpy as np
import logging
FORMAT = '[*] %(asctime)s [%(levelname)s] %(module)s: %(message)s'
DATEFORMAT = '%Y/%m/%d %H:%M:%S'
logging.basicConfig(
    level = logging.INFO,
    format = FORMAT,
    datefmt = DATEFORMAT
)
logger = logging.getLogger('__main__')

def metadataReader(filePath):
    with open(filePath) as js:
        return load(js)

class sounding:
    def __init__(self, path=Path('.'), metaFilePath=Path('.')):
        self.path = path
        self.meta = metadataReader(metaFilePath)
        self.soundingMeta = None
        self.plotMeta     = self.meta["skewT"]

    def reader(self, sounding=None, wdShift=0):
        if(type(sounding)==None):
            logger.error("sounding data empty")
            return

        ## basic variables
        Time_released = sounding[self.soundingMeta["Time"]]
        P_released    = sounding[self.soundingMeta["P"]][:].to_numpy(dtype=float)
        T_released    = sounding[self.soundingMeta["T"]["name"]][:].to_numpy(dtype=float)
        Z_released    = sounding[self.soundingMeta["Z"]][:].to_numpy(dtype=float)
        RH_released   = sounding[self.soundingMeta["RH"]][:].to_numpy(dtype=float)
        lat_released  = sounding[self.soundingMeta["Lat"]][:].to_numpy(dtype=float)
        lon_released  = sounding[self.soundingMeta["Lon"]][:].to_numpy(dtype=float)
        WS_released   = sounding[self.soundingMeta["WS"]["name"]][:].to_numpy(dtype=float)
        WD_released   = ((sounding[self.soundingMeta["WD"]][:] - wdShift)%360).to_numpy(dtype=float)
        ## metpy cal
        TD_released   = dewpoint_from_relative_humidity(T_released * units(f'{self.soundingMeta["T"]["unit"]}'), RH_released/100).m
        U_released, V_released = wind_components(WS_released * units(f'{self.soundingMeta["WS"]["unit"]}'), WD_released * units.degrees)

        # T, P, T, TD, U, V
        data      = np.asarray([P_released,T_released,Z_released,TD_released,RH_released,U_released.to('m/s').m,V_released.to('m/s').m,lat_released,lon_released])
        dataFrame = DataFrame(np.transpose(data),index=Time_released,columns=['P [hPa]','T [degC]','Z [m]','TD [degC]','RH [%]','U [m/s]','V [m/s]','Lat [o]','Lon [o]'])
        return dataFrame, {'P [hPa]':"hPa", 'T [degC]':"degC", 'Z [m]':'m', 'TD [degC]':"degC", 'RH [%]':"percent", 'U [m/s]':'m/s', 'V [m/s]':'m/s', 'Lat [o]':'deg', 'Lon [o]':'deg'}
        # return dataFrame, {'P [hPa]':units.hPa, 'T [degC]':units.degC, 'TD [degC]':units.degC, 'U [m/s]':units('m/s'), 'V [m/s]':units('m/s')}
        # return Time_released, P_released * units.hPa, T_released * units.degreeC, TD_released * units.degreeC, U_released, V_released


class RS41reader(sounding):
    def __init__(self, release_time, path=Path('.'), metaPath=Path('.')):
        super().__init__(path=path,  metaFilePath=metaPath / 'metadata.json')
        self.soundingMeta = self.meta["radio"]["RS41"]

    def read(self, release_time=None):
        self.release_time = release_time
        no_file   = self.path / f"edt2_{self.release_time.strftime('%Y%m%d_%H%M')}.txt"
        logger.info(f"Start reading RS41 {self.release_time}")

        with open(no_file) as rs_file:
            sounding = read_table(rs_file,skiprows=[0,1,2,3,5],delimiter='\s+')
        
        return self.reader(sounding)

class STreader(sounding):
    def __init__(self, no, L0DataPath=Path('.'), metaPath=Path('.')):
        super().__init__(path=L0DataPath, metaFilePath=metaPath / 'metadata.json')
        self.no           = no
        self.soundingMeta = self.meta["radio"]["ST"]

    def L0Reader(self, release_time=None):
        self.release_time = release_time
        no_file = list(self.path.glob(f"no_{self.no}*.csv"))[0]
        logger.info(f"Start reading ST no_{self.no}")

        with open(no_file) as st_file:
            sounding = read_csv(st_file,parse_dates=[0])
        ## timer read
        time          = sounding['Time'][:]
        if(self.release_time != None):
            self.sounding = sounding.loc[sounding[self.soundingMeta["Time"]] >= self.release_time]
        else:
            self.sounding = sounding
        return self.reader(self.sounding, wdShift=180)