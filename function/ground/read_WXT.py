import pandas as pd
import numpy as np
from metpy.units import units
import metpy.calc as mcalc

def read_WXT(data_name):
    ##input dataname : is a string
    ##output Vars is a dataframe
    data = pd.read_csv(data_name, skiprows = (0, 2, 3), parse_dates = ['TIMESTAMP'])
    
    ##pick the data and rename
    Vars = data[['TIMESTAMP', 'airtemp_Avg', 'relhumidity_Avg', 'airpressure_Avg', 'Wsavg_Avg', 'Wdavg_Avg', 
             'WindDir_SD1_WVT']]
    Vars = Vars.rename({'TIMESTAMP':'Time', 'airtemp_Avg':'T', 'relhumidity_Avg':'RH', 
             'airpressure_Avg':'P', 'Wsavg_Avg':'Ws', 'Wdavg_Avg':'Wd', 'WindDir_SD1_WVT':'Wd_std'}, axis = 1)
    ##add Td
    T = Vars['T'][:].to_numpy()
    RH = Vars['RH'][:].to_numpy()
    Td = mcalc.dewpoint_from_relative_humidity(T*units.degC, RH/100).m
    Vars['Td'] = Td
    
    ##add U, V
    ws = Vars['Ws'][:]
    wd = Vars['Wd'][:]
    U = -np.sin(wd/180.*np.pi)*ws
    V = -np.cos(wd/180.*np.pi)*ws
    Vars['U'] = U
    Vars['V'] = V
    
    return Vars