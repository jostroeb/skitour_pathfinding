import sortedcontainers 
from operator import attrgetter
import numpy as np

"""
This is only for testing parts of code, it is neither required nor recommended to be used.
But it could be useful and should be preserved, that is why I have not deleted it.
"""


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


"""array = np.array([[2,3,2],[4,3,8],[4,6,7]])
xypos = [4,3]
cutx = array[(array[:, 0] == xypos[0]) & (array[:, 1] == xypos[1])][0] # Filter x (index 0) column
print(cutx)
print(array[0].size)
"""

import numpy as np
import matplotlib.pyplot as py
from matplotlib import animation

py.close('all') # close all previous plots

# create a random line to plot
#------------------------------------------------------------------------------

x = np.random.rand(40)
y = np.random.rand(40)

py.figure(1)
py.scatter(x, y, s=60)
py.axis([0, 1, 0, 1])
py.show()

# animation of a scatter plot using x, y from above
#------------------------------------------------------------------------------

fig = py.figure(2)
ax = py.axes(xlim=(0, 1), ylim=(0, 1))
scat = ax.scatter([], [], s=60)

def init():
    scat.set_offsets([])
    return scat,

def animate(i):
    data = np.hstack((x[:i,np.newaxis], y[:i, np.newaxis]))
    scat.set_offsets(data)
    return scat,

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(x)+1, 
                               interval=200, blit=False, repeat=False)