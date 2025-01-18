import numpy as np 
import matplotlib.pyplot as plt
from math import inf
import math

def showpath(dataset,patharray,creatednodes = None): # visualizes dataset, printedpath and all searched nodes
    plt.scatter(dataset[:, 0],dataset[:, 1],c = dataset[:, 2],cmap = 'viridis') # plot map with height as color
    if type(creatednodes) == None: # optional argument
        plt.scatter(creatednodes[:, 0],creatednodes[:, 1],c = 'white') # plot path in red on top
    plt.scatter(patharray[:, 0],patharray[:, 1],c = 'red') # plot path in red on top
    ax = plt.gca() # get current axis of plot
    ax.set_aspect('equal', adjustable='box') # setup axis of plot to be equal
    plt.show()

def plotinoriginal(fulldata,reduceddata,patharray = None):
    plt.scatter(fulldata[:, 0], fulldata[:, 1])
    plt.scatter(reduceddata[:, 0],reduceddata[:, 1],c = reduceddata[:, 2],cmap = 'viridis')
    if type(patharray) == None:
        plt.scatter(patharray[:, 0],patharray[:, 1],c = 'red') # plot path in red on top
    ax = plt.gca() # get current axis of plot
    ax.set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == "__main__":
    pass