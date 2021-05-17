import pandas
from pandas import read_csv
from pathlib import Path
from radio.reader import *

import logging
FORMAT = '[*] %(asctime)s [%(levelname)s] %(module)s: %(message)s'
DATEFORMAT = '%Y/%m/%d %H:%M:%S'
logging.basicConfig(
    level = logging.INFO,
    format = FORMAT,
    datefmt = DATEFORMAT
)
logger = logging.getLogger('__main__')

DATA_ROOT = Path('..') / "0401_ObservationData"
ST_DATA   = DATA_ROOT  / "storm tracker"
METADATA  = Path('.')  / "radio"

def readSTLaunchMetaData():
	ST_RootPath = Path('..') / "0401_ObservationData" / "storm tracker"
	ST_launchMetaDataFileName = "20210401_20210406.csv"
	ST_rename = {"NO.":"no", "Time (yyyy/mm/dd HH:MM:SS)":"time"}

	ST_launchMetaData = read_csv(ST_RootPath / ST_launchMetaDataFileName, parse_dates=['Time (yyyy/mm/dd HH:MM:SS)']).dropna(subset=['Time (yyyy/mm/dd HH:MM:SS)']).reset_index(drop=True)
	ST_launchMetaData = ST_launchMetaData[['NO.','Time (yyyy/mm/dd HH:MM:SS)']].rename(columns=ST_rename).astype({'no': 'int32'})

	return ST_launchMetaData

md = readSTLaunchMetaData()


print(md.loc[0]['no'])
print(md.loc[0]['time'])


stObj = STreader(md.loc[0]['no'], L0DataPath=Path(ST_DATA / 'Level 0'), metaPath=METADATA)
P, T, TD, U, V = stObj.L0Reader()