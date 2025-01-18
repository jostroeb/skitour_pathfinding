import numpy as np 
import data_prep
import matplotlib.pyplot as plt
from math import inf
import math
from sortedcontainers import SortedList
import data_prep
import sys
from scipy.spatial import distance
import matplotlib.animation as animation

""" implementation of A* algorithm, partly object oriented
    - takes pandas import, this allows for decent data reduction prior to the actual search algorithm 
    - search algorithm uses heapq for the iterated list
"""



class Node:

    def __init__(self, pos, gscore = inf, fscore = inf, avalanche_score = 1, nontraversable = False): # self references to Node
        self.pos = pos # np array [x,y,z]
        self.gscore = gscore
        self.fscore = fscore
        self.avalanche_score = avalanche_score
        self.nontraversable = nontraversable # for protected natur area, etc.
        self.foundminf = False
        self.inopen = False # to skip compare fscore for newly created nodes 
        self.parent = None # x,y,z [np] arary


    def __lt__(self, compareto): # implements a less than '<' method, which is required for the sortedlist add
        return self.fscore < compareto.fscore
    
#class CreatedNodes:
#    def __init__(self):
#        self.creatednodes = {} # dict to store nodes with pos key

class Openlist:

    def __init__(self): # initialize sortedlist 
        self.list = SortedList()

    def addmultiple(self,nodes):
        #print("now add these nodes to openlist")
        #print(nodes)
        self.list.update(nodes)

    def add(self,node):
        self.list.add(node)

    def count(self,node):
        self.list.count(node)

    def poplowest(self):
        return self.list.pop(0)

    def removeopen(self,node): # remove list of nodes
        self.list.remove(node)
                #except:
                #    raise Exception("Hier ist n doofer Fehler, weil nichtoffene Nodes auf der openList entfernt werden sollen")

    def contains(self, node): # check if position is already included in list
        pass # not implemented yet
        

    def print(self): # debugging method
        for node in self.list:
            print(node)


class AStar:

    def __init__(self, dataset, griddistance = None, max_avalanche_score = 5): # input dataset as pandasobject and griddistance; future remove griddistance
        self.dataset = dataset
        self.griddistance = griddistance
        self.openlist = None # write sortedlist object here, save all open nodes here
        self.creatednodes = {} # dict object creatednodes, save all created notes here, key is position of a node
        self.max_avalanche_score = max_avalanche_score
        self.ncounter = 0


    def closestnode(self, pos, griddistance) -> Node: # find closest values to [x,y] nparray in the dataset and return node    
        if griddistance == None:
            raise Exception("closestnode not implemented for non-grid data yet")
        if type(pos) == list:
            pos = np.array(pos) 

        for searched in [griddistance]: # prefilter to reduce distance calc, future: replace with list or logarithmic growing fnct
            filtered = data_prep.datareduction(self.dataset,pos,filterdistance=searched)
            if filtered.any(): break # break when any points within [x+-searched,y+-searched] rectangle

        if filtered.size == 0: # if no point was found in dataset
            print("no point found within filterdistance: " + str(searched))
            print("consider changing start position or dataset.")
            return

        np.array(pos) # convert pos to np array
        if filtered.size == 3: # if for loop finds single point in dataset
            filtered

        else:
            distances = np.array([[distance.euclidean(pos,point[0:2])] for point in filtered]) # create row vector with hypot lenghts
            filtered = np.concatenate((filtered,distances),1) # add distances to the columns in nparray
            lowestindex = filtered[:, 3].argsort(0)[0] # sort the distances (third) column and return corresponding lowestindex
        return Node(filtered[lowestindex,0:3]) # return lowest
    
    
    def bias(self,slope): # bias tries to improve path for a comfortable walk
        if 0.4663 >= slope >= 0.364:
            return 1
        return 1.1

    def gggg(self,node,z,diagonal,bias = True): # Bias true for optimal path, Bias wrong for accurate length
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

    """write g method with timedistance using gggg and bias"""    
    def getg(self,node1,node2,currentdistance = None):
        if currentdistance == None: # true for non-grid data
            spatialdistance = node1.pos - node2.pos # for future implementation of vector data
            spatialdistance = (abs(spatialdistance[0]),abs(spatialdistance[1]))
            raise Exception("getg not implemented yet for non-grid data")
        else:
            return node1.gscore + currentdistance

    """write heuristics method"""
    def geth(self,node1,node2): # heuristics method for start to end
        h = 0 
        return h # for h=0 runs as Dijkstra

    def getneighbourpos(self, currentnode): # get traversable neighbours when given a node
        dis = self.griddistance
        if dis == None: # for future implementation
            raise Exception("Give distances for grid data or implement other getneighbourpos function for e.g. vectordata")
        else:
            moves = np.array([[dis,0],[-dis,0],[0,-dis],[0,dis],[dis,dis],[-dis,dis],[dis,-dis],[-dis,-dis]])
            neighbourpos = [] # list for easy iteration later
            for move in moves:
                #print(currentnode.pos)
                #print(move)
                newpos = np.add(currentnode.pos[0:2],move) # get neighbour position as 1x2 nparray
                #print(newpos)
                neighbourpos.append(newpos)
            return neighbourpos # 8list with neighbourpos 
    """
            pd = self.dataset[(self.dataset['x'] == newpos[0]) & (self.dataset['y'] == newpos[1])] # wrongggg first filter x, then filter y
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
        #avoid avalanche_ risk zone in g value examination
            return neighbourpos # find neighbours and add to openlist
    """

    def getkey(self, array): # converts array to tuple to make it hashable and therefore usable as a key in a dict
        arr = array[0:2]
        key = tuple(arr)
        return key

    
    # get traversable, non closed nodes, save nodes on edge to creatednodes
    def getnodes(self, neighbourpositions, distances = None): 
        if distances == None: # for future implementation
            raise Exception("Give distances for grid data or implement a new getnodes function for e.g. vectordata (better extend the existing one)")
        nodelist = []
        distancelist = []
        for i,neighbourpos in enumerate(neighbourpositions): # position value for every move direction
            try: # try to find an existing node in creatednodes for current position value
                key = self.getkey(neighbourpos) # get key for lookup in dict
                node = self.creatednodes[key] # lookup in dict

            except: # if no node was created before
                try: # try find data in dataset
                    neighbourpos = self.dataset[(self.dataset[:, 0] == neighbourpos[0]) & (self.dataset[:, 1] == neighbourpos[1])][0] # finds [x,y,z] array for [x,y]
                    node = Node(neighbourpos) # add avalanche score and nontraversable

                except: # otherwise create node with [x,y] and nontraversable = True to avoid lookup in dataset later
                    node = Node(neighbourpos,nontraversable=True)
                    key = self.getkey(neighbourpos)
                    self.creatednodes[key] = node # save non traversable node in creatednodes for avoiding lookup in datset
            if not (node.nontraversable or node.foundminf): # exception for already explored nodes
                nodelist.append(node) # write traversable nodes in return list
            distancelist.append(distances[i])
        return nodelist, distancelist # distancelist has same length as node list and contains corresponding x,y distances
    
    
    def tracepath(self,startnode: Node,endnode: Node) -> list: # follows path from end back to start through jumping to each nodes parent
        current = endnode
        tracepath = [current] # save list of nodes here
        while True:
            if current.pos[0] == startnode.pos[0] and current.pos[1] == startnode.pos[1]:       
                break
            tracekey = self.getkey(current.parent) # create
            node = self.creatednodes[tracekey]
            tracepath.append(node)
            current = node
        return reversed(tracepath)

    
    def visualize(self,path = None, fulldata = None, showsearched = False):
        nodelist = [] # explored nodes
        if showsearched:
            for node in self.creatednodes.values(): # for all nodes in creatednodes
                if not node.nontraversable: # filter out only traversable nodes
                    nodelist.append([node.pos]) # add all positions to a n*3 array
            creatednodes = np.concatenate(nodelist)
        pathlist = [] 
        if type(path) != bool: # when plotting path
            for node in path:
                pathlist.append([node.pos])
            patharray = np.concatenate(pathlist)    
        
        if type(fulldata) != None:
            plt.scatter(fulldata[:, 0], fulldata[:, 1])
        plt.scatter(self.dataset[:, 0],self.dataset[:, 1],c = self.dataset[:, 2],cmap = 'viridis')
        if showsearched:
            plt.scatter(creatednodes[:, 0],creatednodes[:, 1],c = 'white') # plot path in red on top
        if type(path) != None:
            plt.plot(patharray[:, 0],patharray[:, 1],c = 'red') # plot path in red on top
        ax = plt.gca() # get current axis of plot
        ax.set_aspect('equal', adjustable='box')
        plt.show()

    def search(self, startpos, endpos) -> list: # main search algorithm
        startnode = self.closestnode(startpos,self.griddistance) # returns closest point in x,y dimensions
        endnode = self.closestnode(endpos,self.griddistance)
        startnode.gscore = 0
        startnode.fscore = 0 # not really relevant as will be explored first anyways 

        if self.griddistance != None: # setup distance values
            s = self.griddistance
            d = self.griddistance * 1.4142
            distances = [s,s,s,s,d,d,d,d]

        if startnode == endnode or startnode.nontraversable == True:
            raise Exception("Start node not valid as either endnode or non traversable")           

        startnode.foundminf = True # avoids that startnode will be considered as neighbour later
        self.openlist = Openlist() # create instance of openlist

        current = startnode # add first node to openlist
        key = self.getkey(current.pos) # write first node to creatednodes
        self.creatednodes[key] = current
        
        iteration = 0 # counter for search iterations
        while True: # iterate until all end was found or all nodes have been travelled and therefore no path is possible
            iteration += 1

            neighbourpositions = self.getneighbourpos(current) # list of all potential neighbour position as (x,y) tuple, including not possible ones; future: extend above to polygons in vectordataformat
            nodes, currentdistances = self.getnodes(neighbourpositions, distances) # all possible nodes, excluding non traversable
            newopennodes = [] # during iteration save nodes here for append to sortedList; in loop for reset

            for i,node in enumerate(nodes):
                g = self.getg(current,node,currentdistances[i]) # get g using grid distance
                h = self.geth(node,endnode) # heuristics function to calculate distance to enddnode
                new_f = h + g
                if node.inopen:
                    if node.fscore > new_f: # if new connection delivers smaller weight
                        self.openlist.removeopen(node) # remove from open so can be replaced later
                        node.fscore = new_f
                        node.parent = current.pos
                        newopennodes.append(node)
                    else: 
                        continue # nothing has to be changed about node

                else:
                    node.fscore = new_f # for new nodes no fscore existent to compare to
                    node.parent = current.pos # set parent only, if node was not existent before
                    node.inopen = True
                key = self.getkey(node.pos)
                self.creatednodes[key] = node # add node to creatednodes for lookup in next iteration
                newopennodes.append(node) # fill temporary list of opennodes                  
            
            self.openlist.addmultiple(newopennodes) # add list of opennodes, because open were removed earlier and new have been created
            
            current = self.openlist.poplowest() # get next 'current' node with lowest fscore
            current.foundminf = True
            self.creatednodes[self.getkey(current.pos)] = current # replace in creatednodes so node can be skipped later with .foundminf = True

            try: # try to find, if endnode was reached
                endnode = self.creatednodes[self.getkey(endnode.pos)] # if node with position of endnode was created, path was found
                print("Found endnode at iteration: " + str(iteration))
                break # break while loop
            except:
                pass

            if nodes == []: # if even only one node is not explored yet, it might lead to the end
                raise Exception("No path is possible")    
        return self.tracepath(startnode,endnode)
        

def main(directory,griddistance,startpos,endpos):
    extractedcsv = data_prep.getcsv(directory) # get all csv filepaths in directory
    data = data_prep.dataimport(extractedcsv) # get numpy objects of the .csv files
    print("data rows: " + str(data.size))

    reduceddata = data_prep.datareduction(data,startpos,endpos,safteyfactor=2) # reduce dataset for data
    print("reduced dataset for A*: " + str(reduceddata.shape))
    
    astar = AStar(reduceddata,griddistance=griddistance) # give back AStar object, where we next call search method on it
    path = astar.search(startpos,endpos) # returns list of nodes
    
    astar.visualize(path,fulldata = data, showsearched = True)
    pass

if __name__ == "__main__":
    # Test stuff here, not active when importing this code in other script
    testdirectory = r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch'
    griddistance = 5
    startpos = [637212,5264996]
    endpos = [637400,5265200]
    main(testdirectory,griddistance,startpos,endpos)