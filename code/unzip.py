import zipfile
from os import listdir
from os import path
import pandas as pd
import matplotlib as plt

# function takes path and optional amount of files to be extracted starting from top, not looking at previously extracted files 
# namereturn == True returns a list of all the processed files 
def extractfiles(directory,amount = None): 
    directoryraw = r"{}".format(directory) # format the string as raw string
    i = 0
    namelist = []
    if amount is not None:
        amount = amount - 1
    for f in listdir(directoryraw): # for all files in this directory
        name, ext = path.splitext(f)
        if ext == '.zip': # only use .zip files
            if amount is not None:
                if i > amount: # counter for amount of files
                    return(namelist)
                i = i + 1
            fullpath = path.join(directoryraw,f) # create full path of zip file
            with zipfile.ZipFile(fullpath, 'r') as file: # r equals read only, with is exception handler
                file.extractall(directoryraw) # extract zipfile
                for fileending in file.namelist(): # for all files in extracted zipfile
                    namelist.extend([path.join(directoryraw,fileending)]) # extend namelist with full path for each zipfile
    return namelist
    
def createcsv(fileslist):
    namelist = []
    for file in fileslist:
        rawfile = r"{}".format(file)
        with open(rawfile, "r") as text:
            filepath, ext = path.split(rawfile)
            filename, filetype = path.splitext(ext)
            filename = filename + '.csv' # create test.csv
            csv = path.join(filepath,filename) # create C:\...\test.csv
            with open(csv,'w') as csvfile:
                namelist.extend([csv])
                while True:
                    content = text.readline() # reads single lines
                    content = content.replace(' ',';') # create commas for .csv
                    if not content:
                        break # only inner while loop
                    csvfile.writelines(content) # writes each read line
    return namelist    

# move distance is used to calculate the cost estimation h, so a shorter path is preferred
def movedistance(a,b): # accepts two tuples of type (x,y)
    x = abs(a[0] - b[0])
    y = abs(a[1] - b[1])
    max = max(x,y)
    min = min(x,y)
    linear = max - min
    diagonal = min * 1.4142 # aprox. sqrt(2)
    return linear + diagonal
        
        
def getcsv(directory): # get all csv filepaths in directory
    extractedcsv = []
    for f in listdir(directory): # listdir returns filepaths
        name, ext = path.splitext(f)
        if ext == '.csv': # only use .zip files
            extractedcsv.append(path.join(directory,f))
    return extractedcsv

def datareduction(fulldata,start,end, filterdistance = None): # reduces data by selecting rectangle with saftey margin around start and end point
    if filterdistance == None:
        safetydistance = filterdistance
    else: 
        safteyfactor = 1 # keep low (data reduction) but high enough (so optimality is realistic)
        safetydistance = safteyfactor * (abs(start['x'] - end['x']) + abs(start['y'] - end['y'])) # determine Manhattan distance
    cutx = fulldata[(fulldata['x'] > (start['x'] - safetydistance)) & (fulldata['x'] < (start['x'] + safetydistance))] # filter x coordinate
    return cutx[(cutx['y'] > (start['y'] - safetydistance)) & (cutx['y'] < (start['y'] + safetydistance))] # filter y coordinate
    #cutx.info()
    #cuty.info()
    #fulldata.info()

def plotinoriginal(fulldata,reduceddata):
    plt.scatter(fulldata['x'], fulldata['y'])
    plt.scatter(reduceddata['x'],reduceddata['y'],c = reduceddata['z'],cmap = 'viridis')
    #data.plot(x='x', y='y', c='red', kind='scatter')
    #reduceddata.plot(x='x', y='y', c='z', colormap='viridis', kind='scatter')
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    plt.show()

"""create function lawinenscore _____________________"""
def lawinenscore(data): #create function
    lawine = []
    pd.DataFrame()

def extractor():
    directory = input("Write directory without brackets e.g. [C:\Programs\Test\]: ")
    amount = int(input("Export first x files without checking if they already exist: "))
    extracted = extractfiles(directory,amount) # True will return a list of extracted files
    #print(extracted)
    return createcsv(extracted)
    #print("converted .csv files" + extractedcsv)

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

def main():
    directory = r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch'
    amount = 100
    extracted = extractfiles(directory,amount) # True will return a list of extracted files
    extractedcsv = createcsv(extracted)
    dataimport(extractedcsv)

if __name__ == "__main__":
    main()