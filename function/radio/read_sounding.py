import numpy as np
import matplotlib.pyplot as plt
from metpy.plots import SkewT
from metpy.units import units
import metpy.calc as mcalc
import pandas as pd
from pathlib import Path

def read_sounding(r_time, ID):
    #r_time = release time, ex. 2021031210
    #ID is the no. of ST
    file = 'NTU-' + str(r_time) + '.ST_' + str(ID) + 'QC.eol'
    time, P, T, Td, U, V = np.loadtxt(file, skiprows = 14, usecols = (0, 4, 5, 6, 8, 9), unpack = True)
    ##use time as idx to filter out thdaata before release
    P = np.where(P==-999.00, np.nan, P)[time>0]
    T = np.where(T==-999.00, np.nan, T)[time>0]
    Td = np.where(Td==-999.00, np.nan, Td)[time>0]
    U = np.where(U==-999.00, np.nan, U)[time>0]
    V = np.where(V==-999.00, np.nan, V)[time>0]
    
    return P, T, Td, U, V

def plot_sounding(P, T, Td, U, V, r_time, ID):
    ##need the metpy package
    ##from metpy.plots import SkewT
    ##from metpy.units import units
    ##import metpy.calc as mcalc
    fig = plt.figure(figsize=(7, 6))
    skew = SkewT(fig)
    skew.plot(P, T, 'r')
    skew.plot(P, Td, 'g')
    idx = mcalc.resample_nn_1d(P, np.array([1000, 975, 950, 925, 900, 850, 800, 750, 700, 650, 600, 500]))
    skew.plot_barbs(P[idx], U[idx]*units('m/s'), V[idx]*units('m/s'), plot_units = units('m/s'))
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
    

#%%
P, T, Td, U, V = read_sounding(2021031210, 1151)
plot_sounding(P, T, Td, U, V, 2021031210, 1151)