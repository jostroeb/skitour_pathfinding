import zipfile
from os import listdir
from os import path

# function takes path and optional amount of files to be extracted starting from top, not looking at previously extracted files 
def extractfiles(directory,amount = None): # insert directory using r'path' where r equals raw string literal
    abspath = path.abspath(directory)
    i = 0
    amount = amount - 1
    for f in listdir(abspath): # for all files in this directory
        name, ext = path.splitext(f)
        if ext == '.zip': # only use .zip files
            if amount != None:
                if i > amount: # counter for amount of files
                    return(True)
                i = i + 1
            fullpath = path.join(abspath,f) # create full path of zip file
            with zipfile.ZipFile(fullpath, 'r') as file: # r equals read only, with is exception handler
                file.extractall(abspath) # extract zipfil

if __name__ == "__main__":
    extractfiles(r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch',5) 