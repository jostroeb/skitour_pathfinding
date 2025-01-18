import sortedcontainers 
from operator import attrgetter
import numpy as np

class node:
    def __init__(self, f, pos):
        self.f = f
        self.pos = pos

    def __lt__(self,other): # implement less than '<' method, which is used by openset to compare values
        return self.f < other.f
    
    #def __eq__(self,other): # implement equal '=' method, which is used by openset to compare values
    #    return self.pos == other.pos

    #def __hash__(self):
    #    return hash(self.pos)
"""
class opensets:
    def __init__(self):
        self.list = sortedcontainers.SortedList(key=attrgetter("f"))
    
        self.list.update(node)
    def sort(self,node = None):

    def add(self,node):
        self.list.add(node)

    def count(self,node):
        self.list.count(node)

    def poplowest(self):
        return self.list.pop(0)

    def print(self):
        for node in self.list:
            print(node.pos)

    def remove(self,node):
        self.list.remove(node)

"""

"""
openset = opensets()
a = node(1,"posa") # f,pos
b = node(3,"posb")
c = node(2,"posc")
d = node(4,"posd")
openset.add(a)
openset.add(b)
openset.add(c)

list  = []
list.append(a)
list.append(b)
list.append(None)

i = 0

#for member in list:  
    #print(i)
    #print(list[i])
    #i = i + 1

openset.print()
print()

for member in list:
    openset.remove(member)
    openset.print()
    print("\n")
    i = i + 1
    print(i)"""
array = np.array([[2,3,2],[4,3,8],[4,6,7]])
xypos = [4,3]
cutx = array[(array[:, 0] == xypos[0]) & (array[:, 1] == xypos[1])][0] # Filter x (index 0) column
print(cutx)
print(array[0].size)