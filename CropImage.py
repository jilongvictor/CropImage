##################################################################################################
# Crop Image                                                                                     #
#                                                                                                #
# Author: Jilong Li                                                                              #
# Date: 1/14/2020                                                                                #
# Contact: jilong@broadinstitute.org                                                             #
#                                                                                                #
##################################################################################################

#!/usr/bin/python3

import sys
import os
import math
import numpy as np
import PySimpleGUI as sg

#pip install pysimplegui

layout = [[sg.Graph(canvas_size=(600, 600), graph_bottom_left=(0, 0), graph_top_right=(600, 600), background_color='white', enable_events=True, key='graph', change_submits=True,   drag_submits=True)],
          [sg.Text('Enter input file', size=(12, 1)), sg.InputText('C:\\jilong\\crop_bead\\input.txt', size=(69, 10))],
          [sg.Text('Enter output file', size=(12, 1)), sg.InputText('C:\\jilong\\crop_bead\\output.txt', size=(69, 10))],
          [sg.Text('* Input file should contain at lease 3 columns: 0 - x, 1 - y, 2 - color scale number (e.g. # UMIs)')],
          [sg.Text('* Output file contains a list of binary numbers: 1 - selected, 0 - removed')],
          [sg.Button('Load'), sg.Button('Remove'), sg.Button('Cancel'), sg.Button('Save'), sg.Button('Exit')]]

window = sg.Window('Crop Image', layout, finalize=True)

graph = window['graph']
pre = (-1, -1)           # the previous point
boundary_x = {}          # dictionary for each x in ROI
boundary_y = {}          # dictionary for each y in ROI
x_min,x_max = 100000,-1  # x boundary of ROI
y_min,y_max = 100000,-1  # y boundary of ROI

while True:
    event, values = window.read()
    mouse = values['graph']
    if event in ('graph', 'graph+UP'):
        m0 = int(mouse[0])  # use integer to represent points
        m1 = int(mouse[1])
        if pre == (-1, -1): # this is a new drawing, reset variables and dictionaries
            x_min,x_max = 100000,-1
            boundary_x.clear()
            y_min,y_max = 100000,-1
            boundary_y.clear()
        else: # draw a line between two continuous points
            line = graph.draw_line((m0,m1), pre, color='red')
        if m0 in boundary_x.keys():  # put x,y into x dictionary
            boundary_x[m0].append(m1)
        else:
            boundary_x[m0] = [m1]
        if m1 in boundary_y.keys():  # put x,y into y dictionary
            boundary_y[m1].append(m0)
        else:
            boundary_y[m1] = [m0]
        if abs(pre[0] - m0) > 1:    # add missing points between the current point and the previous one for x
            a = min(pre[0], m0)
            b = max(pre[0], m0)
            c = min(pre[1], m1)
            d = max(pre[1], m1)
            if (m1 - pre[1] >= 0 and m0 - pre[0] >= 0) or (m1 - pre[1] <= 0 and m0 - pre[0] <= 0):
                flag = 1
            else:
                flag = -1
            for i in range(a+1, b, 1):
                if i not in boundary_x.keys():
                    if flag == 1:
                        boundary_x[i] = [c + abs(int((d-c)*(i-a)/(b-a)))]
                    else:
                        boundary_x[i] = [d - abs(int((d-c)*(i-a)/(b-a)))]
                else:
                    if flag == 1:
                        boundary_x[i].append(c + abs(int((d-c)*(i-a)/(b-a))))
                    else:
                        boundary_x[i].append(d - abs(int((d-c)*(i-a)/(b-a))))
        if abs(pre[1] - m1) > 1:    # add missing points between the current point and the previous one for y
            a = min(pre[1], m1)
            b = max(pre[1], m1)
            c = min(pre[0], m0)
            d = max(pre[0], m0)
            if (m1 - pre[1] >= 0 and m0 - pre[0] >= 0) or (m1 - pre[1] <= 0 and m0 - pre[0] <= 0):
                flag = 1
            else:
                flag = -1
            for i in range(a+1, b, 1):
                if i not in boundary_y.keys():
                    if flag == 1:
                        boundary_y[i] = [c + abs(int((d-c)*(i-a)/(b-a)))]
                    else:
                        boundary_y[i] = [d - abs(int((d-c)*(i-a)/(b-a)))]
                else:
                    if flag == 1:
                        boundary_y[i].append(c + abs(int((d-c)*(i-a)/(b-a))))
                    else:
                        boundary_y[i].append(d - abs(int((d-c)*(i-a)/(b-a))))
        x_min = min(x_min, m0)
        x_max = max(x_max, m0)
        y_min = min(y_min, m1)
        y_max = max(y_max, m1)
        if event == 'graph+UP':
            pre = (-1, -1)
        else:
            pre = [m0, m1]
    elif event == 'Save':   # output a list of numbers: 1 - selected, 0 - removed
        with open(values[1], "w") as outfile:
            for i in range(len(selected)):
                outfile.write(str(selected[i])+"\n")
        outfile.close()
    elif event == 'Load':   # load bead image from the input file
        x = np.loadtxt(values[0], delimiter='\t', dtype='float', usecols=(0))
        y = np.loadtxt(values[0], delimiter='\t', dtype='float', usecols=(1))
        umis = np.loadtxt(values[0], delimiter='\t', dtype='int', usecols=(2))
        maxv = math.log(umis[0],2)/255
        scale = max(max(x), max(y))/500
        if maxv == 0:
            maxv = 1
        selected = np.tile(1, len(x))
        for i in range(len(x)):
            v = int(math.log(umis[i],2)/maxv)
            point = graph.draw_point((x[i]/scale+50, y[i]/scale+50), 1, color=sg.RGB(255-v, 255-v, 0))
    elif event in ('Remove', 'Cancel'):
        for i in range(len(x)):
            x1 = int(x[i]/scale+50)
            y1 = int(y[i]/scale+50)
            if x1 >= x_min and x1 <= x_max and y1 >= y_min and y1 <= y_max: # if the current point is within the boundaries of the ROI
                disx,disy = 100000,100000
                x2,y2 = -1,-1
                for bpx in boundary_x.keys():   # find the nearest x in the ROI
                    if abs(bpx - x1) < disx:
                        disx = abs(bpx - x1)
                        x2 = bpx
                ply = boundary_x[x2]
                for bpy in boundary_y.keys():   # find the nearest y in the ROI
                    if abs(bpy - y1) < disy:
                        disy = abs(bpy - y1)
                        y2 = bpy
                plx = boundary_y[y2]
                if x1 >= min(plx) and x1 <= max(plx) and y1 >= min(ply) and y1 <= max(ply): # if the current point is in the ROI
                    if event == 'Remove':
                        selected[i] = 0
                        point = graph.draw_point((x[i]/scale+50, y[i]/scale+50), 1, color='white')
                    elif event == 'Cancel':
                        selected[i] = 1
                        v = int(math.log(umis[i],2)/maxv)
                        point = graph.draw_point((x[i]/scale+50, y[i]/scale+50), 1, color=sg.RGB(255-v, 255-v, 0))
    elif event in (None, 'Exit'):	# close window or click Exit
        break

window.close()
