import zipfile
from os import listdir
from os import path

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
                #i = 0
                while True:
                    #if i > 10: debugging option to only execute for first 10 lines
                    #    print("b")
                    #    break
                    #i = i + 1
                    #print(i)
                    content = text.readline() # reads single lines
                    content = content.replace(' ',';') # create commas for .csv
                    #print(content)
                    if not content:
                        break # only inner while loop
                    csvfile.writelines(content) # writes each read line
    return namelist    



if __name__ == "__main__":
    directory = input("Write directory without brackets e.g. [C:\Programs\Test\]: ")
    amount = int(input("Export first x files without checking if they already exist: "))
    extracted = extractfiles(directory,amount) # True will return a list of extracted files
    #print(extracted)
    extractedcsv = createcsv(extracted)
    #print("converted .csv files" + extractedcsv)