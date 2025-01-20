import numpy as np 
import data_prep
import matplotlib.pyplot as plt
from math import inf
from sortedcontainers import SortedList
import data_prep
from scipy.spatial import distance

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
        self.v = 0


    def __lt__(self, compareto): # implements a less than '<' method, which is required for the sortedlist add
        return self.fscore < compareto.fscore

    #def __eq__(self, compareto): # this doesn't resolve remove exception
    # be aware the list has to be have an absolute order, so __lt__ and __eq__ must not rely solely on different arguments !!!
    #    return self.fscore == compareto.fscore and self.pos[0] == compareto.pos[0] and self.pos[1] == compareto.pos[1] 
    

class Openlist:

    def __init__(self): # initialize sortedlist 
        self.list = SortedList()
        self.exceptcounter = []

    def addmultiple(self,nodes): # to add multiple nodes to openlist
        self.list.update(nodes)

    def count(self,node):
        self.list.count(node)

    def poplowest(self):
        return self.list.pop(0)

    def removeopen(self,node): # remove list of nodes
        try:
            self.list.remove(node)
        except:
            #print("unresolved nasty except at pos" + str(node.pos))
            self.exceptcounter.append(node.pos)
            # it cannot remove an object from self.list, but only objects in the list can reach this point ???

    def len(self):
        return len(self.list)

    def print(self): # debugging method
        for node in self.list:
            print(node)


class AStar:

    def __init__(self, dataset, griddistance = None): # input dataset as pandasobject and griddistance; future remove griddistance
        self.dataset = dataset
        self.griddistance = griddistance
        self.openlist = None # write sortedlist object here, save all open nodes here
        self.creatednodes = {} # dict object creatednodes, save all created notes here, key is position of a node
        self.max_avalanche_score = 5
        self.ncounter = 0
        self.vmax = 20


    def closestnode(self, pos, griddistance) -> Node: # find closest values to [x,y] nparray in the dataset and return node    
        if griddistance == None:
            raise Exception("closestnode not implemented for non-grid data yet")
        if type(pos) == list:
            pos = np.array(pos) 

        for searched in [griddistance,griddistance*2,griddistance*5,griddistance*10,griddistance*100]: # prefilter to reduce distance calc, future: replace with list or logarithmic growing fnct
            filtered = data_prep.datareduction(self.dataset,pos,filterdistance=searched)
            if filtered.any(): break # break when any points within [x+-searched,y+-searched] rectangle

        if filtered.size == 0: # if no point was found in dataset
            raise Exception("no point found within filterdistance: " + str(searched))
            return

        np.array(pos) # convert pos to np array
        if 2 < filtered.size < 5: # if for loop finds single point in dataset
            filtered

        else:
            distances = np.array([[distance.euclidean(pos,point[0:2])] for point in filtered]) # create row vector with hypot lenghts for x,y
            filtered = np.concatenate((filtered,distances),1) # add distances to the columns in nparray
            lowestindex = filtered[:, 3].argsort(0)[0] # sort the distances (third) column and return corresponding lowestindex
        return Node(filtered[lowestindex,0:3]) # return lowest
        

    def getkey(self, array): # converts array to tuple to make it hashable and therefore usable as a key in a dict
        arr = array[0:2] # get x,y values
        key = tuple(arr)
        return key


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


    def getnodes(self, neighbourpositions, distances = None): # get traversable, non closed nodes, save nodes on edge to creatednodes
        if distances == None: # for future implementation
            raise Exception("Give distances for grid data or implement a new getnodes function for e.g. vectordata (better extend the existing one)")
        nodelist = []
        distancelist = []
        for i,neighbourpos in enumerate(neighbourpositions): # position value for every move direction
            try: # try to find an existing node in creatednodes for current position value
                node = self.creatednodes[self.getkey(neighbourpos)] # lookup in dict with created key

            except: # if no node was created before
                try: # try find data in dataset
                    neighbourpos = self.dataset[(self.dataset[:, 0] == neighbourpos[0]) & (self.dataset[:, 1] == neighbourpos[1])][0] # finds [x,y,z] array for [x,y]
                    node = Node(neighbourpos[0:3],avalanche_score=neighbourpos[3]) # add avalanche score and nontraversable

                except: # otherwise create node with [x,y] and nontraversable = True to avoid lookup in dataset later
                    node = Node(neighbourpos[0:3],nontraversable=True)
                    self.creatednodes[self.getkey(node.pos)] = node # save non traversable node in creatednodes for avoiding lookup in datset
                    continue

            if not (node.nontraversable or node.foundminf): # exception for already explored nodes
                if node.avalanche_score <= self.max_avalanche_score: # skip nodes with higher avalanche score
                    nodelist.append(node) # write traversable and avalanche okay nodes in return list
                    distancelist.append(distances[i]) # append distancelist

                else: # with current avalanchescore is this node not okay, but will be saved in creatednodes anyways for faster lookup
                    self.creatednodes[self.getkey(node.pos)] = node # do not append to nodelist, as not relevant for further search
                    continue

        if len(nodelist) != len(distancelist): # only if implementation error
            raise Exception("nodelist and distancelist have to be of equal length")
        return nodelist, distancelist # distancelist has same length as node list and contains corresponding x,y distances
    

    def bias(self,slope): # bias tries to improve path for a comfortable walk
        if slope > 0.4663: return 1
        else: return 1.1


    def getg(self,node1,node2,currentdistance = None,bias = True): # set bias = False for time calculation of finished route
        if currentdistance == None: # true for non-grid data
            spatialdistance = node1.pos - node2.pos # for future implementation of vector data
            spatialdistance = (abs(spatialdistance[0]),abs(spatialdistance[1]))
            raise Exception("getg not implemented yet for non-grid data")
            
        else:
            vneu = 0
            b_law = 1 + 0.1* (node2.avalanche_score - 1) # bias for avalanche score
            th = currentdistance * 0.72 # equals distance * 3600s/h / 5000m/h, time horizontal move
            delta_z = node2.pos[2] - node1.pos[2]
            if delta_z >= 0: # for going uphill
                slope = delta_z / currentdistance # positive for going uphill
                if slope > 1: k = 3
                else: k = 1
                tv = delta_z * 9.0000 # equals delta_z [m] * 3600s/h / 400m/h, time uphill vertical move
                if bias: 
                    edgeweight = b_law * k * self.bias(slope) * (0.5 * min(th,tv) + max(th,tv)) # with all bias included
                else:
                    edgeweight = k * (0.5 * min(th,tv) + max(th,tv)) # only for calculation of exact pathlength
            else:
                #"""
                delta_z = abs(delta_z)
                k = 1
                eta = 0.95 # efficiency
                v0 = node1.v # previous speed
                delta_v = np.sqrt(18.62 * delta_z) # 2 * 9.81m/s^2 * deltaz from energy equation
                delta_l = distance.euclidean(node1.pos[0:3],node2.pos[0:3]) 
                vcurr = v0 + delta_v # current speed
                if vcurr > 20:
                    k = 3
                vneu = min(eta * vcurr,self.vmax) # new speed
                edgeweight = k * delta_l / min(vcurr,self.vmax)
                #"""
                #edgeweight = abs(delta_z * 3.6) # coarse schmudlach model; equals delta_z * 3600s/h / 1000m/h, time vertical downhill move
            return (node1.gscore + edgeweight), vneu


    def geth(self,node1,endnode): # heuristics method for start to end distance(cannot overestimate, therefore)
        if type(self.griddistance) == None:
            raise Exception("Distance estimate for non-grid data not implemented yet")
        else:
            horizontaldistance = data_prep.movedistance(node1.pos,endnode.pos) # movedistance is shortest path in 8-grid world, otherwise use scipy distance
            h,x = self.getg(node1,endnode,currentdistance = horizontaldistance, bias = True)
            return h # for h=0 runs as Dijkstra


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
        plt.close('all')
        nodelist = [] # explored nodes
        #plt.ion()
        if showsearched:
            for node in self.creatednodes.values(): # for all nodes in creatednodes
                if not node.nontraversable: # filter out only traversable nodes
                    nodelist.append([node.pos]) # add all positions to a n*3 array
            creatednodes = np.concatenate(nodelist)
        pathlist = []
        if type(path) != None: # when plotting path
            for node in path:
                try:
                    pathlist.append([node.pos])
                except:
                    print(("pathlist object had no path"))
            patharray = np.concatenate(pathlist)    
        
        if type(fulldata) != None:
            plt.scatter(fulldata[:, 0], fulldata[:, 1])
        plt.scatter(self.dataset[:, 0],self.dataset[:, 1],marker='s',c = self.dataset[:, 2],cmap = 'viridis')
        if showsearched:
            plt.scatter(creatednodes[:, 0],creatednodes[:, 1],c = 'white') # plot path in red on top
        lawinenscore1 = self.dataset[self.dataset[:,3] > 1]
        plt.scatter(lawinenscore1[:, 0],lawinenscore1[:, 1],marker='s',c = 'm') # plot lawinennodes in pinks
        if type(path) != None:
            plt.plot(patharray[:, 0],patharray[:, 1],c = 'red') # plot path in red on top
        ax = plt.gca() # get current axis of plot
        ax.set_aspect('equal', adjustable='box')
        plt.show()


    def search(self, startpos, endpos,max_avalanche_score = 5) -> list: # main search algorithm
        self.max_avalanche_score = max_avalanche_score
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

        key = self.getkey(startnode.pos) # write first node to creatednodes
        self.creatednodes[key] = startnode
        current = startnode # add first node to openlist

        iteration = 0 # counter for search iterations
        while True: # iterate until all end was found or all nodes have been travelled and therefore no path is possible
            neighbourpositions = self.getneighbourpos(current) # list of all potential neighbour position as (x,y) tuple, including not possible ones; future: extend above to polygons in vectordataformat
            nodes, currentdistances = self.getnodes(neighbourpositions, distances) # all possible nodes, excluding non traversable
            newopennodes = [] # during iteration save nodes here for append to sortedList; in loop for reset

            for i,node in enumerate(nodes):
                g, v = self.getg(current,node,currentdistances[i]) # get g using grid distance
                h = self.geth(node,endnode) # heuristics function to calculate distance to enddnode
                new_f = g + h
                if node.inopen:
                    if node.fscore > new_f: # if new connection delivers smaller weight
                        self.openlist.removeopen(node) # remove from open so can be replaced later
                        node.gscore = g
                        node.fscore = new_f
                        node.parent = current.pos
                        node.v = v
                        newopennodes.append(node) # remove or else adds double duplicates
                    else: 
                        continue # nothing has to be changed about node

                else:
                    node.gscore = g
                    node.fscore = new_f # for new nodes no fscore existent to compare to
                    node.parent = current.pos # set parent only, if node was not existent before
                    node.inopen = True
                    node.v = v

                key = self.getkey(node.pos)
                self.creatednodes[key] = node # add node to creatednodes for lookup in next iteration
                newopennodes.append(node) # fill temporary list of opennodes                  
            
            iteration += 1
            self.openlist.addmultiple(newopennodes) # add list of opennodes, because open were removed earlier and new have been created
            
            current = self.openlist.poplowest() # get next 'current' node with lowest fscore, removes from openlist
            current.foundminf = True
            self.creatednodes[self.getkey(current.pos)] = current # replace in creatednodes so node can be skipped later with .foundminf = True

            if self.getkey(current.pos) == self.getkey(endnode.pos): # if endnnode was found
                print("Found endnode at iteration: " + str(iteration))
                break # break while loop

            if self.openlist.len() < 1: # if even only one node is not explored yet, it might lead to the end
                raise Exception("No path is possible")    # if no more open nodes, but also endnode not found, no path is possible
        print("Exceptcounter: " + str(len(self.openlist.exceptcounter)))
        return self.tracepath(startnode,current)
        

    def findpath(self,startpos,endpos):
        max_avalanche_score = 1
        while True: # runs algorithm until 
            if max_avalanche_score > 5:
                    raise Exception("No path was found at highest avalanche level")
            try:
                path = self.search(startpos,endpos,max_avalanche_score = max_avalanche_score) # returns list of nodes
                return path
            except:
                max_avalanche_score += 1
                pass


def main(directory,griddistance,startpos,endpos):
    extractedcsv = data_prep.getcsv(directory) # get all csv filepaths in directory
    data = data_prep.dataimport(extractedcsv) # get numpy objects of the .csv files
    print("data rows: " + str(data.size))

    reduceddata = data_prep.datareduction(data,startpos,endpos,safteyfactor=2) # reduce dataset for data
    print("reduced dataset for A*: " + str(reduceddata.shape))

    reduceddata = data_prep.lawinenscore(reduceddata,griddistance = griddistance, startpoints = [[637077.5,5264987.5],[637177.5,5264997.5]],size = 6)
    
    astar = AStar(reduceddata,griddistance=griddistance) # give back AStar object, where we next call search method on it

    path = astar.search(startpos,endpos)
    #print("pathlength:" + len(path))
    pathdata = path
    #path = astar.findpath(startpos,endpos)
    data_prep.export_to_kml(path, 'waypoints.kml')
    astar.visualize(path=pathdata,fulldata = data)


if __name__ == "__main__":
    # Test stuff here, not active when importing this code in other script
    testdirectory = r'C:\Users\ZOJSTROE\OneDrive - Carl Zeiss AG\Studium\T3100 - Studienarbeit\Karten\Karte_Garmisch_full'
    griddistance = 5

    #startpos = [654632,5256010] # start tour osterfelderkopf - alpspitze
    #endpos = [654450,5254955] # end tour osterfelderkopf - alpspitze
    #endpos = [654437,5255803] # small tour osterfelderkopf - seitlicher hügel
    #endpos = [654637,5255993] # small

    startpos = [650428,5253866] # zugspitze gipfeltour
    endpos = [650299,5254362]

    startpos = [643574,5265843] # kreuzspitze niedriger
    endpos = [643921,5265641] # kreuzspitze

    #startpos = [650428,5253866] # kleiner testlauf zugspitze
    #endpos = [650400,5253840]

    #startpos = [654632,5256010] # tour osterfelderkopf - alpspitze
    #startpos = [637020,5264996] # alternative start
    #endpos = [654600,5255980] # alternative end
    #endpos = [637230,5265040] # end
    main(testdirectory,griddistance,startpos,endpos)