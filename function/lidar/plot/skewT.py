# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 00:58:16 2021

@author: Admin
"""

import glob
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from metpy.units import units

station = 'Sunsing'

file = glob.glob(f'Stormtracker_{station}/*.eol')
# ind = [11, 14, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32] # Yilan
# ind = [0, 5, 10, 12, 14, 15, 16, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34] # Wuyuan
# ind = [0, 5, 9, 12, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34] # Suaou
ind = [3, 5, 6, 9, 11, 12, 14, 15, 16, 19, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34] # Sunsing
# file = np.delete(file, ind)
n = np.size(file)

for i in ind:
    print(f'file = {i:02d}')
    p, T, Td, u, v, wd = np.loadtxt(file[i], skiprows = 14, usecols = (4, 5, 6, 8, 9, 11), unpack = True)
    
    df = pd.DataFrame({'pressure': p,
                       'temperature': T,
                       'dewpoint': Td,
                       'Uwind': u,
                       'Vwind': v,
                       'Wspd': wd})
    
    p  = df['pressure'].values * units.hPa
    T  = df['temperature'].values * units.degC
    Td = df['dewpoint'].values * units.degC
    u  = df['Uwind'].values * units.meter / (units.second)
    v  = df['Vwind'].values * units.meter / (units.second)
    
    # lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    # parcel_prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    
    fig = plt.figure(figsize=(11, 8.5))
    skew = SkewT(fig, rotation = 45)
    
    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot
    skew.plot(p, T, 'r', linewidth=3)
    skew.plot(p, Td, 'g', linewidth=3)
    skew.plot_barbs(p[::100], u[::100], v[::100])
    skew.ax.set_ylim(1020, 300)
    skew.ax.set_xlim(-20, 40)
    skew.ax.tick_params(labelsize = 24.)
    skew.ax.set_xlabel('temperature ($\degree C$)', linespacing = 7, fontsize = 24.)
    skew.ax.set_ylabel('pressure ($hPa$)', linespacing = 4, fontsize = 24.)
    skew.ax.set_title('Skew-T Log-P Diagram' + '\n' + '$_{station:}$ $_{' + station + '}$' '   $_{local}$ $_{time:}$ $_{' + file[i][29:33] + '/' + file[i][33:35] + '/' + file[i][35:37] + '}$' + ' $_{' + file[i][37:39] + ':00}$', verticalalignment = 'bottom', fontsize = 30.)
    '''
    # Plot LCL temperature as black dot
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    
    # Plot the parcel profile as a black line
    skew.plot(p, parcel_prof, 'k', linewidth=3)
    
    # Shade areas of CAPE and CIN
    skew.shade_cin(p, T, parcel_prof, Td)
    skew.shade_cape(p, T, parcel_prof)
    '''
    # Plot a zero degree isotherm
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=3)
    
    # Add the relevant special lines
    skew.plot_dry_adiabats(linewidth=2.5)
    skew.plot_moist_adiabats(linewidth=2.5)
    skew.plot_mixing_lines(linewidth=2.5)
    
    # Show the plot
    plt.savefig(f'skewT_{file[i][29:39]}.png', dpi = 300)
    plt.show()
