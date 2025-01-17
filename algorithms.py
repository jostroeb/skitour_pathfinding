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
import data_prep
import sys

""" implementation of A* algorithm, partly object oriented
    - takes pandas import, this allows for decent data reduction prior to the actual search algorithm 
    - search algorithm uses heapq for the iterated list
"""



class Node:

    def __init__(self, pos, z = 0, gscore = inf, fscore = inf, avalanche_score = 1, nontraversable = False): # self references to Node
        self.pos = pos
        self.z = z
        self.gscore = gscore
        self.fscore = fscore
        self.avalanche_score = avalanche_score
        self.nontraversable = nontraversable # for protected natur area, etc.
        self.foundminf = False
        self.inopen = False # to skip compare fscore for newly created nodes 
        self.parent = None


    def __lt__(self, compareto): # implements a less than '<' method, which is required for the sortedlist add
        return self.fscore < compareto.fscore
    
    #verboten
    #def __eq__(self, compareto): # implements an equality method for later checking, if node already checked
     #   return self.pos == compareto.pos

#class CreatedNodes:
#    def __init__(self):
#        self.creatednodes = {} # dict to store nodes with pos key

class Openlist:

    def __init__(self): # initialize sortedlist 
        self.list = SortedList()

    def addmultiple(self,nodes):
        self.list.update(nodes)

    def add(self,node):
        self.list.add(node)

    def count(self,node):
        self.list.count(node)

    def poplowest(self):
        return self.list.pop(0)

    def removeopen(self,nodes): # remove list of nodes
        for node in nodes:
            if node == None or node.inopen == True:
                pass
            else:
                try:
                    self.list.remove(node)
                except:
                    raise Exception("Hier ist n doofer Fehler, weil nichtoffene Nodes auf der openList entfernt werden sollen")

    def contains(self, node): # check if position is already included in list
        pass # not implemented yet
        

    def print(self): # debugging method
        for node in self.list:
            print(node.fscore)


class AStar:

    def __init__(self, pdvalues, griddistance = None, max_avalanche_score = 5): # input dataset as pandasobject and griddistance; future remove griddistance
        self.pdvalues = pdvalues
        self.griddistance = griddistance
        self.openlist = None # write sortedlist object here, save all open nodes here
        self.creatednodes = {} # dict object creatednodes, save all created notes here, key is position of a node
        self.max_avalanche_score = max_avalanche_score
        self.poscounter = 0 # for grid layout

    def closestnode(self, pos): # find closest values to (x,y) pos tuple in the dataset and return node
        """solution is not very elegant, as for non kartesian grid, results might not be optimal"""
        start = {'x': [pos[0]],'y': [pos[1]],'z': [0.1]}
        startdata = pd.DataFrame(start)
        print(startdata.head)
        for d in [1,2,3,4,5,10,15,20,30,50]:
            try:
                filtered = data_prep.datareduction(self.pdvalues,startdata,filterdistance=d)
            except:
                pass
            if not filtered.empty:
                return filtered
        return            
        smallestx = self.pdvalues.iloc[(self.pdvalues['x'] - pos[0]).abs().argsort()[:1]]['x']
        #(self.pdvalues[]-)[smallestx]
        #smallesty = self.pdvalues.iloc[(self.pdvalues['y'] - pos[1]).abs().argsort()[:1]]
        
        return (smallestx,smallesty)
    
        difference = difference['y'] - pos[0]
        minvalueforx = filteredx.min()
        minx_entries = self.pdvalues[minvalueforx]

        filteredy = filteredx['y'] - pos[1]
        node = Node((filteredvalues['x'],filteredvalues['y']))
        return node
    
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
    def getg(self,node1,node2):
        if self.griddistance == None: 
            spatialdistance = node1.pos - node2.pos # for future implementation of vector data
            spatialdistance = (abs(spatialdistance[0]),abs(spatialdistance[1]))
            # implement calculation for timedistance
        else:
            if self.poscounter > 3:
                return 1.4142
            else:
                return 1
                edgeweight = 1
                g = node1.g + edgeweight
                return g

    """write heuristics method"""
    def geth(self,node1,node2): # heuristics method for start to end
        h = 0 
        return h # for h=0 runs as Dijkstra

    def getneighbourpos(self, currentnode): # get traversable neighbours when given a node
        nodedistance = self.griddistance
        if nodedistance == None: # for future implementation
            raise Exception("Give distances for grid data or implement other getneighbourpos function for e.g. vectordata")
        else:
            moves = [(nodedistance,0),(-nodedistance,0),(0,nodedistance),(0,-nodedistance),(nodedistance,nodedistance),(-nodedistance,-nodedistance),(nodedistance,-nodedistance),(-nodedistance,nodedistance)]
            neighbourpos = []
            for move in moves:
                print(currentnode.pos)
                newpos = np.add(currentnode.pos,move) # get neighbour position as (x,y) tuple
                print(newpos)
                neighbourpos.append(newpos)
            return neighbourpos # 8list with neighbourpos as (x,y) tuple
    """
            pd = self.pdvalues[(self.pdvalues['x'] == newpos[0]) & (self.pdvalues['y'] == newpos[1])] # wrongggg first filter x, then filter y
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

    def getnodes(self, node, neighbourpositions, distances = None):
        """check if position is existent in database, future implement to add a node, which is not traversable for improved efficiency"""
        #implement node return with node.nontraversable = True for edgenodes
        if distances == None: # for future implementation
            raise Exception("Give distances for grid data or implement a new getnodes function for e.g. vectordata (better extend the existing one)")
        getexplored = []
        getunexploredpos = []
        for neighbourpos in neighbourpositions:
            try:
                getexplored.append(self.creatednodes[neighbourpos]) # check node dictionary for already existent node
            except:
                self.pdvalues
                getunexploredpos.append(neighbourpos)
        return getexplored, getunexploredpos
    
    #finished
    def tracepath(self,startnode,endnode): # follows path from end back to start through jumping to each nodes parent
        current = endnode
        tracepath = []
        while True:
            tracepath.append(current)
            next = current.parent
            current = next
            if current == startnode:
                tracepath.append(current)
                break            
        return tracepath.reverse()


    def search(self, startpos, endpos): # main search algorithm
        startnode = startpos
        endnode = endpos
        #startnode = AStar.closestnode(startpos)
        #endnode = AStar.closestnode(endpos)
        startnode.gscore = 0
        startnode.fscore = 0 # not relevant, as node will be explored first anyways

        if startnode == endnode:
            print("Start is End")
            return

        startnode.foundminf = True # avoids that startnode will be considered as neighbour later
        
        self.openlist = Openlist() # create instance of openlist

        current = startnode # add first node to openlist
        self.openlist.add(endnode)
        
        if self.griddistance != None:
            s = self.griddistance
            d = self.griddistance * 1.4142
            distances = [s,s,s,s,d,d,d,d]

        n = 0

        print(sys.getsizeof(self))

        while True:
            n = n + 1
            print(n)
            if n == 10000:
                print("openlist:")
                print(sys.getsizeof(self.openlist))
                print("creatednotes:")
                print(sys.getsizeof(self.creatednodes))
                break
            self.openlist.print()
            print("\n")
            newnodes = [] # during iteration save newly created nodes here, where fscore comparsion is not necessary; in loop for reset
            neighbourpositions = self.getneighbourpos(current) # list of all potential neighbour position as (x,y) tuple, including not possible ones
            # future: extend above to polygons in vectordataformat
            explorednodes, unexploredpos = self.getnodes(current, neighbourpositions, distances) # 8list of possible nodes, including impossible edgenodes as non traversable, 8list unexplored pos
            
            for unexplored in unexploredpos: # detection if no possible path exists
                if unexplored != None: # if even only one node is not explored yet, it might lead to the end
                    break
                else: # only for readability, can be removed
                    raise Exception("No path is possible")

            self.openlist.removeopen(explorednodes) # try remove all items of explored nodes from openlist, else pass
            for pos in unexploredpos:
                if pos != None:
                    newnode = Node(pos)
                    newnodes.append(newnode)
                else:
                    newnodes.append(None)
            #nodes = explorednodes.append(newnodes) # has to be in correct order for positions
            #print(explorednodes)
            #print(newnodes)
            
            for nodelist in [explorednodes, newnodes]:
                self.poscounter = 0 # diagonal moves if pos > 4
                #print("nodelist")
                #print(nodelist)
                #if nodelist == []:
                #    print("empty nodelist")
                #    continue
                newopennodes = [] # during iteration save nodes here for append to sortedList; in loop for reset
                for i,node in enumerate(nodelist):
                    self.poscounter = i
                    if node == None:
                        print("continue")
                        continue # skip empty slot but increase poscounter for later knowledge if step in grid is straight or diagonal

                    else:
                        if node.foundminf or node.nontraversable or self.max_avalanche_score < node.avalanche_score:
                            print("skipped node because foundminf, nontraversable or max_avalanche_score")
                            self.creatednodes[node.pos] = node # add node to created nodes for lookup in next iteration
                            continue # skip node

                        g = self.getg(current,node) # using poscounter to know if diagonal or not for grid
                        h = self.geth(node,endnode) # heuristics function to calculate distance to enddnode
                        new_f = h + g
                        if node.inopen:
                            if node.fscore > new_f: # if new connection delivers smaller weight
                                node.fscore = new_f
                                node.parent = current
                            else: # improves readability, can be removed for efficiency
                                pass # will later be added back to openlist
                        else:
                            node.fscore = new_f # for new nodes no fscore existent to compare to
                            node.parent = current # set parent only, if node was not existent before
                            node.inopen = True
                    self.creatednodes[node.pos] = node # add node to creatednodes for lookup in next iteration
                    newopennodes.append(node) # fill list of opennodes                   
            self.openlist.addmultiple(newopennodes) # add list of opennodes, because open were removed earlier and new have been created

            current.foundminf = True    
            current = self.openlist.poplowest()
            if current == endnode:
                print("Found endnode")
                break # break while loop
        
        #self.tracepath(startnode,endnode) # returns path as string
        #print("foundpath")        

"""bis hier ist code gut                    
            
    neighbourpos = self.getneighbourpos(current, 5) # 5 neighbourdistance
    for neighbourpos in neighbourpos:
        try: #check if node is already in open, how can I compare a node, which might be slightly different, due to numerics error or so
            neighbour = creatednodes[neighbourpos]
            if neighbour.inopen:
                openlist.remove()
        except:
            Node(neighbourpos,)
        openlist.add(neighbourpos)
    current = openlist.poplowest()
    openlist.remove(current)
"""

def main():
    directory = r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch'
    extractedcsv = data_prep.getcsv(directory)
    reduceddata = data_prep.dataimport(extractedcsv) # pandas dataobject
    startline = 20
    endline = 200
    reduceddata = data_prep.datareduction(reduceddata,reduceddata.iloc[startline],reduceddata.iloc[endline]) # example values
    griddistance = 5
    #reduceddata = createavalanche_score(reduceddata)
    #plotinoriginal(data,reduceddata) # check if data is reduced correctly
    start = (reduceddata.iloc[startline,0],reduceddata.iloc[startline,1])
    #reduceddata.MultiIndex.from_tuples(,None)
    end = (reduceddata.iloc[endline,0],reduceddata.iloc[endline,1])
    """
    print("start")
    print(start)
    print("end")
    print(end)
    """
    print(reduceddata.head)
    astar = AStar(reduceddata,griddistance=griddistance) # give back AStar object, where we next call search method on it
    #print(sys.getsizeof(astar))
    #findclose = (637042.1,5264982.2)
    x = reduceddata.iloc[startline,0]
    y = reduceddata.iloc[startline,1]
    z = reduceddata.iloc[startline,2]
    startnode = Node((x,y),z)
    x = reduceddata.iloc[endline,0]
    y = reduceddata.iloc[endline,1]
    z = reduceddata.iloc[endline,2]
    endnode = Node((x,y),z)
    astar.search(startnode,endnode)
    #print(sys.getsizeof(astar))
    #print(findclose)
    #foundnode = astar.closestnode(findclose)
    #print("output")
    #print(foundnode)
    #print(foundnode.z)
    #path = astar.search()

if __name__ == "__main__":
    # Test stuff here, not active when importing this code in other script
    main()
