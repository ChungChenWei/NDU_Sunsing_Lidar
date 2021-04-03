# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 00:58:16 2021

@author: Admin
"""

import shapefile
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from descartes import PolygonPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from metpy.units import units

fname = r'twcounty/twcounty'

shp = shapefile.Reader(fname)
rec = shp.records()
shapes = shp.shapes()

# file = 'edt2_20210402_0300.txt'
file = '46000-2021040206.edt.txt'

# p, T, Td, ws, wd = np.loadtxt(file, skiprows = 6, usecols = (3, 4, 6, 8, 7), unpack = True)
p, T, RH, ws, wd = np.loadtxt(file, delimiter = ',', skiprows = 3, usecols = (2, 3, 4, 5, 6), unpack = True)

e = 6.112*np.exp((17.67*T)/(T + 243.5))*(RH/100)
r = 0.622*(e)/(p - e)*1000.
# e = mpcalc.vapor_pressure(1000. * units.mbar, mixing)

df = pd.DataFrame({'pressure': p,
                   'temperature': T,
                   'r': r,
                   'speed': ws,
                   'direction': wd})

p  = df['pressure'].values * units.hPa
T  = df['temperature'].values * units.degC
r  = df['r'].values * units('g/kg')
e = mpcalc.vapor_pressure(p, r)
Td = mpcalc.dewpoint(e)
wind_speed = df['speed'].values * units.meter / (units.second)
wind_dir = df['direction'].values * units.degrees
u, v = mpcalc.wind_components(wind_speed, wind_dir)

lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
lfc_pressure, lfc_temperature = mpcalc.lfc(p, T, Td)
parcel_prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
cape, cin = mpcalc.cape_cin(p, T, Td, parcel_prof)

fig = plt.figure(figsize = (12., 9.))
fig.subplots_adjust(top = 0.9, bottom = 0.1, left = 0.05, right = 0.96, wspace = 0.08, hspace = 0.25)
gs = gridspec.GridSpec(21, 5)
skew = SkewT(fig, subplot = gs[:, :4],rotation = 45)

# Plot the data using normal plotting functions, in this case using
# log scaling in Y, as dictated by the typical meteorological plot
skip = 100
skew.plot(p, T, 'r', linewidth=3)
skew.plot(p, Td, 'g', linewidth=3)
skew.plot_barbs(p[::skip], u[::skip], v[::skip])
skew.ax.set_ylim(1020, 100)
skew.ax.set_xlim(-40., 40.)
skew.ax.tick_params(labelsize = 22.)
skew.ax.set_xlabel('temperature ($\degree C$)', linespacing = 7, fontsize = 22.)
skew.ax.set_ylabel('pressure ($hPa$)', linespacing = 4, fontsize = 22.)
skew.ax.set_title(f'Sounding   Time: {file[6:10]}/' + f'{file[10:12]}/' + f'{file[12:14]} ' + f'{file[14:16]}Z', loc = 'left', va = 'bottom', fontsize = 26.)

# Plot LCL temperature as black dot
skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

# Plot the parcel profile as a black line
skew.plot(p, parcel_prof, 'k', linewidth=3)

# Shade areas of CAPE and CIN
skew.shade_cin(p, T, parcel_prof, Td)
skew.shade_cape(p, T, parcel_prof)

# Plot a zero degree isotherm
skew.ax.axvline(0, color='c', linestyle='--', linewidth=3)

# Add the relevant special lines
skew.plot_dry_adiabats(linewidth=2.5)
skew.plot_moist_adiabats(linewidth=2.5)
skew.plot_mixing_lines(linewidth=2.5)

ax1 = fig.add_subplot(gs[0:7, 4])
h = Hodograph(ax1, component_range = 50.)
h.add_grid(increment = 12.5)
h.plot(u, v, color = '#0080ff')
ax1.tick_params(labelsize = 15.)
ax1.set_xticks(np.arange(-50., 75., 25.))
ax1.set_yticks(np.arange(-50., 75., 25.))
ax1.set_xticklabels([])
ax1.set_title('Hodograph', fontsize = 20.)
ax1.set_xlabel('wind speed ($m$ $s^{-1}$)', fontsize = 15.)
ax1.set_ylabel('wind speed ($m$ $s^{-1}$)', fontsize = 15.)

ax2 = fig.add_subplot(gs[9:15, 4])
[ax2.add_patch(PolygonPatch(shape, fc= 'none')) for shape in shapes]
# ax2.scatter(lon[10:], lat[10:], c = 'r', s = 10)
ax2.tick_params(labelsize = 15.)
ax2.set_xticks(np.arange(119.5, 122., 0.5))
ax2.set_yticks(np.arange(22., 24.5, 0.5))
ax2.set_xticklabels(['', '120°E', '', '121°E', ''])
ax2.set_yticklabels(['22°N', '', '23°N', '', '24°N'])
ax2.set_xlim([119.5, 121.5])
ax2.set_ylim([22, 24])
ax2.grid(linestyle = '--')
ax2.set_title('Trajectory', fontsize = 20.)
ax2.set_xlabel('longitude',  fontsize = 15.)
ax2.set_ylabel('latitude', fontsize = 15.)

ax3 = fig.add_subplot(gs[17:, 4])
# ax3.text(121., 23.1, '$P_{0}$=' + f'{p[0].magnitude:.1f} $hPa$', fontsize = 15.)
# ax3.text(121., 22.8, '$T_{0}$=' + f'{T[0].magnitude:.1f} $°C$', fontsize = 15.)
# ax3.text(121., 22.5, '$T_{d_{0}}$=' + f'{Td[0].magnitude:.1f} $°C$', fontsize = 15.)
# ax3.text(121., 22.2, '$LCL$=' + f'{lcl_pressure.magnitude:.1f} $hPa$', fontsize = 15.)
# ax3.text(121., 21.9, '$LFC$=' + f'{lfc_pressure.magnitude:.1f} $hPa$', fontsize = 15.)
# ax3.text(121., 21.6, '$CAPE$=' + f'{cape.magnitude:.1f}' + ' $J$ $kg^{-1}$', fontsize = 15.)
# ax3.text(121., 21.3, '$CIN$=' + f'{cin.magnitude:.1f}' + ' $J$ $kg^{-1}$', fontsize = 15.)

ax3.text(0.03, 0.75, '$LCL$=' + f'{lcl_pressure.magnitude:.1f} $hPa$', fontsize = 15.)
ax3.text(0.03, 0.55, '$LFC$=' + f'{lfc_pressure.magnitude:.1f} $hPa$', fontsize = 15.)
ax3.text(0.03, 0.35, '$CAPE$=' + f'{cape.magnitude:.1f}' + ' $J$ $kg^{-1}$', fontsize = 15.)
ax3.text(0.03, 0.15, '$CIN$=' + f'{cin.magnitude:.1f}' + ' $J$ $kg^{-1}$', fontsize = 15.)
ax3.set_xticks([])
ax3.set_yticks([])

# Show the plot
plt.savefig(f'skewT_{file[6:16]}.png', dpi = 300)
plt.show()
