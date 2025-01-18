#import geopandas.datasets
import unzip
import utm
import geopandas as gpd
import pandas as pd
import numpy as np
import geodatasets
import matplotlib.pyplot as plt
from os import listdir
from os import path
# check venv !!!!!!!!!!!!!!!!!!

def dataimport(list):
    #input = geopandas.read_file(list[0])
    df = pd.read_csv(list[0],names=['x','y','z'],sep=';',dtype=np.float32)
    frames = [pd.read_csv(list[i],names=['x','y','z'],sep=';',dtype=np.float32) for i in range(0,len(list))]
#    for i in range(0,len(list)):
#        print(i)
#        input = pd.read_csv(list[i],names=['x','y','z'],sep=';',dtype=np.float32)
        #print(list[0])
        #input.info()
    df = pd.concat(frames, ignore_index=True)
    #full.drop(-9999.00)
    #input.concat(input2,'outer')
    df.info()
    dfsmall = df[df['z'] > -9998.00]
    dfsmall.info()
    df.head()
    return dfsmall

    
    label = dfsmall.loc[(df['x'] == 6.370125e+05) & (df['y'] == 5.2649975e+06)]
    print(label)
    
    #input.GeoDataFrame.rename_geometry('xy', inplace=True))
    #input.plot()
    #input.plot()
    #nybb = geopandas.read_file(geodatasets.get_path("nybb"))
    #nybb.explore()
    
    
    
    #data.head()
    #data.plot()
    #for textfile in list:
    #    content = open(textfile, "r")
        

if __name__ == "__main__":
    #directory = input("Write directory without brackets e.g. [C:\Programs\Test\]: ")
    #amount = int(input("Export first x files without checking if they already exist: "))
    directory = r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch'
    amount = 100
    extracted = unzip.extractfiles(directory,amount) # True will return a list of extracted files
    extractedcsv = unzip.createcsv(extracted)
    # extractedcsv = []
    # for f in listdir(directory): # for all files in this directory
    #     name, ext = path.splitext(f)
    #     if ext == '.csv': # only use .zip files
    #         extractedcsv.append(path.join(directory,f))
    #extractedcsv = [r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch\637_5264.csv',r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch\637_5265.csv']
    dataimport(extractedcsv)