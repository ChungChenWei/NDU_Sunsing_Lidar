import numpy as np
import matplotlib.pyplot as plt
from metpy.plots import SkewT
from metpy.units import units
import metpy.calc as mcalc
import pandas as pd
from pathlib import Path

release_time = np.array(['2020/11/20 08:28:00', '2020/11/20 09:32:00', '2020/11/20 18:30:00', '2020/11/20 15:32:00',
                         '2020/11/20 17:10:00', '2020/11/21 15:30:00', '2020/11/21 09:30:00', '2020/11/20 20:00:00',
                         '2020/11/20 00:00:00', '2020/11/21 17:00:00', '2020/11/21 02:00:00', '2020/11/20 00:00:00',
                         '2020/11/21 08:00:00', '2020/11/21 12:40:00', '2020/11/21 11:00:00', '2020/11/20 23:00:00',
                         '2020/11/21 05:00:00', '2020/11/21 18:30:00', '2020/11/21 06:42:00', '2020/11/21 14:00:00',
                         '2020/11/20 12:32:00', '2020/11/20 11:20:00', '2020/11/20 14:00:00'])

#data
rootpath = Path('./merged_data')
files = sorted(rootpath.glob('*.csv'))

def read_sounding_noQC(ID, r_time):
    File = 'no_' + str(ID) + '.csv'
    sounding = pd.read_csv(File, parse_dates = ['Time'])
    
    ##########################################################################
    #series
    time = sounding['Time'] > str(r_time) #.to_numpy(dtype=float)
    T_released = sounding['Temperature(degree C)'][time].to_numpy(dtype=float)
    RH_released = sounding['Humidity(%)'][time].to_numpy(dtype=float)
    P_released = sounding['Pressure(hPa)'][time].to_numpy(dtype=float)
    WS_released = sounding['Speed(km/hr)'][time].to_numpy(dtype=float)
    WD_released = sounding['Direction(degree)'][time].to_numpy(dtype=float) -180*units.degrees
    #z = sounding['Height(m)'].to_numpy(dtype=float)
    Td_released = mcalc.dewpoint_from_relative_humidity(T_released*units.degC, RH_released/100).m
    
    u_released, v_released = mcalc.wind_components(WS_released * units.km/units.hr, WD_released * units.degrees)
    
    return P_released, T_released, Td_released, u_released, v_released
 
    
def plot_sounding_noQC(P, T, Td, U, V, r_time, ID):
    ##need the metpy package
    ##from metpy.plots import SkewT
    ##from metpy.units import units
    ##import metpy.calc as mcalc
    fig = plt.figure(figsize=(7, 6))
    skew = SkewT(fig)
    skew.plot(P, T, 'r')
    skew.plot(P, Td, 'g')
    idx = mcalc.resample_nn_1d(P, np.array([1000, 975, 950, 925, 900, 850, 800, 750, 700, 650, 600, 500]))
    skew.plot_barbs(P[idx], U[idx], V[idx], plot_units = units('m/s'))
    ##special lines
    skew.plot_dry_adiabats() 
    skew.plot_moist_adiabats(color = 'blue') 
    skew.plot_mixing_lines(p = np.linspace(1100, 300)*units.hPa)
    ##title etc.,
    plt.title(str(ID) + '_' + str(r_time) + 'LST')
    plt.xlim(-40, 40) 
    plt.ylim(1100, 300)
    for i in range(-70, 40, 20):
        plt.fill_between(range(i, i+11), 1100, 300, color = '#C4FF8C')
    
    #plt.savefig('merged_data_plot/' + fname + '.png')
    plt.show()
