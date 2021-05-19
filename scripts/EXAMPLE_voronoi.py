#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 16:13:27 2021

@author: alexlindgrenruby
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial import ConvexHull, convex_hull_plot_2d


def read_position_data(N_Fish,N_Data_Files,N_Frames,Series_Name):
    #Function read_position_data() takes input paramaters for the series 'Series_Name'
    #and outputs an arrays containing the X and Y postiion data for that series.

    #Notes to make sure this works: N_Frames is important--make sure it's the actual number
    #of frames in the *whole* sample (not just for one "fish") otherwise you will get errors
    
    X = np.zeros((N_Fish,N_Frames)) 
    Y = np.zeros((N_Fish,N_Frames))
    
    if type(Series_Name) != str:
        print('Series_Name must be a string \n Thanks!')
        return

    for index in range(N_Data_Files):
        #Each iteration of this for loop corrosponds to one fish file, which
        #contains 1-dimensional arrays for position in x and y. 
        
        #Loads file and assignes data to fish_data
        filename = Series_Name + '_fish%g' % index + '.npz'
        fish_data = np.load(filename, allow_pickle=True)

        active_frames = fish_data['frame']
        if len(active_frames) != N_Frames:
            #Checks for activity across all observation frames. 
            #A discrepency here indicates tracking errors. 
            num_pixels = np.zeros(N_Frames)
            fish_X = np.zeros(N_Frames)
            fish_Y = np.zeros(N_Frames)

            for i in range(len(active_frames)):
                #Assignes fish position data to fish_X and fish_Y only on 
                #active frames
                num_pixels[int(active_frames[i])] = fish_data['num_pixels'][i]
                fish_X[int(active_frames[i])] = fish_data['X'][i]
                fish_Y[int(active_frames[i])] = fish_data['Y'][i]
        else:
            #If no tracking issues, assignes position data to fish_X and fish_Y
            num_pixels = fish_data['num_pixels']
            fish_X = fish_data['X']
            fish_Y = fish_data['Y']
            
        for i in range(N_Frames):
            #Iterates through all frames of obsfervation. 
            check = True
            if num_pixels[i] < np.inf:
                #Checks for real fish by only allowing finite pixel size. 
                for j in range(N_Fish):
                    #For each "real" position data, variable "check" makes sure
                    #the point isn't written multiple times. (check = False 
                    #indicates the position is already written and prevents
                    #further writing) Then writes position into X and Y on the 
                    #appropriate frame. 
                    if X[j,i] == 0 and Y[j,i] == 0 and check == True:
                        X[j,i] = fish_X[i]
                        Y[j,i] = fish_Y[i]
                        check = False
   
    #statement communicates status of tracking.     
    statement = 'Tracking issues detected, see missing[] for details.' 
    flag = True
    missing = []
    for i in range(N_Frames): 
        for j in range(N_Fish):
            if X[j,i] == Y[j,i] == 0:
                missing.append(i)
                #statement = statement + ' %g' % i
                flag = False
    if flag:
        print('All fish accounted for!')
    else:
        print(statement)
        
    #outputs position and missing frames
    Position = X,Y,missing
    return Position



N_Fish = 30
N_Data_Files = 82
N_Frames = 720
Series_Name = 'series 1'

P = read_position_data(N_Fish,N_Data_Files,N_Frames,Series_Name)
X = P[0]
Y = P[1]

density_record = []
area_record = []
perimeter_record = []
for j in range(N_Frames):
    x = []
    y = []
    density = []
    if j not in P[2]:
        for i in range(N_Fish):
            x.append(X[i][j])
            y.append(-Y[i][j])
        
        points = []
        for k in range(N_Fish):
            points.append([x[k],y[k]])
        vor = Voronoi(points)
        hull = ConvexHull(points)
        
        for m in range(len(vor.regions)):
            vertices = []
            if -1 not in vor.regions[m] and vor.regions[m] != []:
                for n in range(len(vor.regions[m])):
                    vertices.append([vor.vertices[vor.regions[m][n],0],
                                    vor.vertices[vor.regions[m][n],1]])
                Area = ConvexHull(vertices).volume
                if Area != 0 and Area <= hull.volume:
                    density.append((1/Area))
                    density_record.append((1/Area))
                    perimeter_record.append(ConvexHull(vertices).area)
                    area_record.append(Area)
                
                Density = np.average(density)
                
        #plotting - only use if you want to output the voronoi or convex hull
        #animation. Quote out either the voronoi or convex hull portion, which-
        #ever you don't intend to use. 
        
        """
        #voronoi plotting
        tag = ' Voronoi_Animation_frame'
        fig = plt.figure(figsize=(8, 6)) 
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1]) 
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        voronoi_plot_2d(vor, ax1, show_vertices=False,
                              line_colors='orange', line_width=3,
                              line_alpha=0.6, point_size=4)
        ax2.bar(1,Density,width=.8)
        ax1.set_xlim(0,30)
        ax1.set_ylim(-30,0)
        ax2.set_ylim(0,1)
        
        #convex hull plotting
        tag = ' ConvexHull_Animation_frame'
        convex_hull_plot_2d(hull)
        plt.title('Convex Hull Animation')
        
        picturename = Series_Name + tag + '%g' % j
        plt.savefig(picturename)
        plt.close('all')
        """
        
si = np.average(perimeter_record)/(np.average(area_record)**(1/2))