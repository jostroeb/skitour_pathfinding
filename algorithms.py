import numpy as np 
import fastkml
import utm
import data_prep
from os import listdir
from os import path
import pandas as pd
import matplotlib.pyplot as plt
from math import inf
from sortedcontainers import SortedList

""" implementation of A* algorithm, partly object oriented
    - takes pandas import, this allows for decent data reduction prior to the actual search algorithm 
    - search algorithm uses heapq for the iterated list
"""

class Node:

    def __init__(self, pos, z = 0, gscore = inf, fscore = inf, lawinescore = 1): # self references to Node
        self.pos = pos
        self.z = z
        self.gscore = gscore
        self.fscore = fscore
        self.lawinescore = lawinescore
        self.explored = False
        self.inopen = False # to check when adding new neighbour nodes, if they already exist in open
        self.parent = None


    def __lt__(self, compareto): # implements a less than '<' method, which is required for the sortedlist add
        return self.f < compareto.f
    
    #verboten
    #def __eq__(self, compareto): # implements an equality method for later checking, if node already checked
     #   return self.pos == compareto.pos

class Openlist:

    def __init__(self):# open list 
        self.list = SortedList()

    def addmultiple(self,nodes):
        self.list.update(nodes)

    def add(self,node):
        self.list.add(node)

    def count(self,node):
        self.list.count(node)

    def poplowest(self):
        return self.list.pop(0)

    def remove(self,node): # remove a node
        self.list.remove(node)
        node.explored = True

    def contains(self, node): # check if position is already included in list
        pass # not implemented yet
        

    def print(self): # debugging method
        for node in self.list:
            print(node.f)


class AStar:

    def __init__(self, pdvalues):
        self.pdvalues = pdvalues

    def closestnode(self, pos, gscore, fscore): # find closest values in the dataset and return node
        filteredvalues = self.pdvalues[self.pdvalues[() & ()]]
        node = Node((filteredvalues['x'],filteredvalues['y']), gscore, fscore)
        return node
    
    def bias(self,slope): # bias tries to improve path for a comfortable walk
        if 0.4663 >= slope >= 0.364:
            return 1
        return 1.1

    def getg(self,node,z,diagonal,bias = True): # Bias true for optimal path, Bias wrong for accurate length
        if diagonal == 1:
            th = 0.7200 # equals 1m * 3600s/h / 5000m/h
        else:
            th = 1.0182 # equals 1.4142m * 3600s/h / 5000m/h 
        z_diff = z - node.z
        if z_diff >= 0:
            slope = z_diff / diagonal # positive for going uphill
            tv = z_diff * 9.0000 # equals z_diff [m] * 3600s/h / 400m/h
            if bias:
                edgeweight = self.bias(slope) * (0.5 * min(th,tv) + max(th,tv))
            else:
                edgeweight = (0.5 * min(th,tv) + max(th,tv))
        else:
            edgeweight = abs(z_diff * 3.6) # equals Z_diff * 3600s/h / 1000m/h
            return node.f + edgeweight

    def getneighbours(self, currentnode, nodedistance): # get neighbours when given a node
        moves = [(nodedistance,0),(-nodedistance,0),(0,nodedistance),(0,-nodedistance),(nodedistance,nodedistance),(-nodedistance,-nodedistance),(nodedistance,-nodedistance),(-nodedistance,nodedistance)]
        neighbours = []
        diagonalcounter = 0
        diagonal = 1
        for move in moves:
            diagonalcounter = diagonalcounter + 1
            if diagonalcounter > 4:
                diagonal = 1.4142
            newpos = currentnode.pos + move # get neighbour position
            pd = self.pdvalues[(self.pdvalues['x'] == newpos[0]) & (self.pdvalues['y'] == newpos[1])] # returns corresponding pdvalues row
            if pd:
                print("neighbour not existent")
                continue # skips incase pd is not existent
            pd_z = pd['z']
            z_diff = pd_z - currentnode.z
            if (diagonal == 1 & 1 < z_diff) or (diagonal != 1 & 1.4142 < z_diff): # skip nodes with slope > 100%
                print("neighbour too steep")
                continue
            neighbour_z = pd['z'] # selects z column of pd
            g = self.getg(currentnode,pd_z,diagonal) # returns weight of neighbournode
            f = g + movedistance(currentnode.pos,newpos) # estimate
            neighbournode = Node(newpos,neighbour_z,g,f)
            neighbournode.parent = currentnode
            neighbours.append(neighbournode)
        """avoid lawine risk zone in g value examination"""
        return neighbours # find neighbours and add to openlist
    
    def search(self, start, end): # main search algorithm
        startnode = AStar.closestnode(start, 0, )
        endnode = AStar.closestnode(end, inf, inf)

        startnode.explored = True # avoids that startnode will be considered as neighbour later

        if startnode == endnode:
            return
        
        openlist = Openlist() # create instance of openlist

        current = startnode # add first node to openlist

        while True:
            if current == endnode:
                print("Start is End")
                break

            neighbours = self.getneighbours(current, 5) # 5 neighbourdistance
            for neighbour in neighbours:
                if neighbour.inopen: """check if node is already in open, how can I compare a node, which might be slightly different, due to numerics error or so"""
                
                    openlist.add(neighbour)
            current = openlist.poplowest()
            openlist.remove(current)

        reversepath = []

        while True:
            if current == startnode:
                break
            reversepath.append(current)
            current = current.parent


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

def datareduction(fulldata,start,end): # reduces data by selecting rectangle with saftey margin around start and end point
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

def lawinenscore(data):
    lawine = []
    pd.DataFrame()

def main():
    directory = r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch'
    extractedcsv = getcsv(directory)
    data = data_prep.dataimport(extractedcsv) # pandas dataobject
    reduceddata = datareduction(data,data.iloc[1],data.iloc[20000]) # example values
    reduceddata = lawinenscore(reduceddata)
    #plotinoriginal(data,reduceddata) # check if data is reduced correctly
    start = (reduceddata.iloc[1])
    end = (reduceddata.iloc[20000]['x'],reduceddata.iloc[20000]['y'])

    print(start)
    print(end)
    
    #astar = AStar(reduceddata) # give back AStar object, where we next call search method on it
    #path = astar.search()

if __name__ == "__main__":
    # Test stuff here, not active when importing this code in other script
    main()
