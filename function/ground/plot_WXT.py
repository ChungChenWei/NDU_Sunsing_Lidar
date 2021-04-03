from read_WXT import read_WXT
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import numpy as np
from time import *

fname = '../../data/WXT/CR1000_Data1min_2021040317LST.dat'

def plot_WXT(fname):

    df = read_WXT(fname)
    fig, ax = plt.subplots(3, 1, sharex = 'col')

    ax[0].plot(df['T'], 'r-')
    ax[0].plot(df['Time'][:], df['Td'][:], 'g-')
    ax[0].set_ylabel('($^oC$)')
    
    ax[1].plot(df['Time'][:], df['P'][:], 'k-')
    ax[1].set_ylabel('(mb)')
    
    itv = 100   ##interval for quiver
    ax[2].quiver(df['Time'][::itv], 0.5, df['U'][::itv], df['V'][::itv], scale = 10, scale_units = 'inches')
    ax[2].xaxis.set_major_formatter(mdate.DateFormatter('%m/%d\n%H:%M:%S'))
    ax[2].get_yaxis().set_visible(False)
    plt.suptitle('WXT')
    

def plot_WXT_daily_mean(fname):
    df = read_WXT(fname).resample('D', on = 'Time').mean().reset_index()
    
    fig, ax = plt.subplots(3, 1, sharex = 'col')

    ax[0].plot(df['Time'][:], df['T'][:], 'r-')
    ax[0].plot(df['Time'][:], df['Td'][:], 'g-')
    ax[0].set_ylabel('($^oC$)')
    
    ax[1].plot(df['Time'][:], df['P'][:], 'k-')
    ax[1].set_ylabel('(mb)')
    
    itv = 1   ##interval for quiver
    ax[2].quiver(df['Time'][::itv], 0.5, df['U'][::itv], df['V'][::itv], scale = 10, scale_units = 'inches')
    ax[2].xaxis.set_major_formatter(mdate.DateFormatter('%m/%d\n%H:%M:%S'))
    ax[2].get_yaxis().set_visible(False)
    plt.suptitle('WXT, daily_mean')
        
##%
plot_WXT(fname)
plot_WXT_daily_mean(fname)