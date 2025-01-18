import zipfile
from os import listdir
from os import path
import pandas as pd
import matplotlib as plt
import numpy as np
import sys

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
    

def createcsv(fileslist): # create .csv files from .txt files
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


def getcsv(directory): # get all csv filepaths in directory
    extractedcsv = []
    for f in listdir(directory): # listdir returns filepaths
        name, ext = path.splitext(f)
        if ext == '.csv': # only use .zip files
            extractedcsv.append(path.join(directory,f))
    return extractedcsv


# reduces data, either around a two points or within a given distance filterdistance
def datareduction(fulldata, startpos, endpos = None, filterdistance: float = None,safteyfactor = 1) -> np.array:
    if type(endpos) is None and filterdistance is None:
        raise Exception("Either endpos or filterdistance has to be given")
    if filterdistance is not None: # filter data around one point
        safetydistance = filterdistance
    else: # filter data around two points
        safetydistance = safetyfactor * (abs(startpos[0] - endpos[0]) + abs(startpos[1] - endpos[1]))  # Using indices 0 and 1 for x and y
        print("Considered safteymargin to find optimal path: " + str(safetydistance))
    
    cutx = fulldata[(fulldata[:, 0] > (startpos[0] - safetydistance)) & (fulldata[:, 0] < (startpos[0] + safetydistance))] # Filter x (index 0) column
    reduceddata = cutx[(cutx[:, 1] > (startpos[1] - safetydistance)) & (cutx[:, 1] < (startpos[1] + safetydistance))] # Filter y (index 1) column 
    return reduceddata


def movedistance(a,b): # accepts two tuples of type (x,y), approximate
    x = abs(a[0] - b[0])
    y = abs(a[1] - b[1])
    max = max(x,y)
    min = min(x,y)
    linear = max - min
    diagonal = min * 1.4142 # aprox. sqrt(2)
    return linear + diagonal

"""create function lawinenscore _____________________"""
def lawinenscore(data): # add lawinenscore in some area, for test
    lawine = []
    

def extractor(): # extraction tool for user input
    directory = input("Write directory without brackets e.g. [C:\Programs\Test\]: ")
    amount = int(input("Export first x files without checking if they already exist: "))
    extracted = extractfiles(directory,amount) # True will return a list of extracted files
    return createcsv(extracted) # return list of createdcsv files


def dataimport(file_list) -> np.array: 
    data_arrays = []  # Save data arrays here
    for file in file_list:
        # Load the data from .csv file
        data = np.genfromtxt(file, delimiter=';', dtype=np.float64)  # Read only the first three columns
        data_arrays.append(data)
    
    combined_data = np.concatenate(data_arrays)  # Combine all data arrays
    
    filtered_data = combined_data[combined_data[:,2] > -9998.00]  # Filter rows where the third column (z) is greater than -9998.00

    # Print the information about the combined and filtered data
    print(f"Combined data shape: {combined_data.shape}")
    print(f"After removing values outside of country borders: {filtered_data.shape}")

    # Return the filtered data as a np array
    return filtered_data


def main():
    directory = r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch'
    amount = 100
    extracted = extractfiles(directory,amount) # extract .zip files
    extractedcsv = createcsv(extracted) # create .csv files

if __name__ == "__main__":
    main()