import matplotlib as mil
mil.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline 
import sys 
import numpy as np
class Basegraph(object):
    def __init__(self,x_values,y_values, Ylabel, Xlabel,Title):
        self.Y_label = Ylabel
        self.X_label = Xlabel
        self.show_grid = True
        self.title = Title
        self.x_values = x_values
        self.y_values = y_values
        
    # Start of user code -> properties/constructors for Basegraph class

    # End of user code
    def show(self):
        # Start of user code protected zone for show function body
        plt.plot(self.x_values, self.y_values, 'y-')
        plt.xlabel(self.X_label)
        plt.ylabel(self.Y_label)
        plt.title(self.title)
        plt.grid(self.show_grid)
        plt.show()
    def plotyy(x1,y1,x2,y2):
        fig, ax1 = plt.subplots()
        ax1.plot(x1, y1, 'b-')
        for tl in ax1.get_yticklabels():
            tl.set_color('b')
        ax2 = ax1.twinx()
        ax2.plot(x2, y2, 'r.')
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        plt.title('Courbe I-V (bleu) et P-V (rouge)')
        return ax1,ax2
    def operating_point(self,Ipan,Vpan,Ipump,Vpump,Ms,Mp):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x1=Vpan*Ms
        y1=Ipan*Mp
        x2=Vpump
        y2=Ipump
        ax.plot(x1, y1, color='lightblue',linewidth=3, marker='s')
        ax.plot(x2, y2, color='darkgreen', marker='^')
        y_lists = y1[:]
        y_lists = y_lists.tolist()
        y_lists.extend(y2)
        y_dist = max(y_lists)/10
        x_lists = x1[:]
        x_lists = x_lists.tolist()
        x_lists.extend(x2)  
        x_dist = max(x_lists)/1000
        division = 1000
        x_begin = min(x1[0], x2[0])     # 3
        x_end = max(x1[-1], x2[-1])     # 8
        points1 = [t for t in zip(x1, y1) if x_begin<=t[0]<=x_end] 
        points2 = [t for t in zip(x2, y2) if x_begin<=t[0]<=x_end] 
        x_axis = np.linspace(x_begin, x_end, division)
        idx = 0
        id_px1 = 0
        id_px2 = 0
        x1_line = []
        y1_line = []
        x2_line = []
        y2_line = []
        xpoints = len(x_axis)
        intersection = []
        while idx < xpoints:
            # Iterate over two line segments
            x = x_axis[idx]
            if id_px1>-1:
                if x >= points1[id_px1][0] and id_px1<len(points1)-1:
                    y1_line = np.linspace(points1[id_px1][1], points1[id_px1+1][1], 1000)
                    x1_line = np.linspace(points1[id_px1][0], points1[id_px1+1][0], 1000)
                    id_px1 = id_px1 + 1
            if id_px1 == len(points1):
                x1_line = []
                y1_line = []
                id_px1 = -1
            if id_px2>-1:
                if x >= points2[id_px2][0] and id_px2<len(points2)-1:
                    y2_line = np.linspace(points2[id_px2][1], points2[id_px2+1][1], 1000)
                    x2_line = np.linspace(points2[id_px2][0], points2[id_px2+1][0], 1000)
                    id_px2 = id_px2 + 1
            if id_px2 == len(points2):
                x2_line = []
                y2_line = []
                id_px2 = -1
            idx+= 1
        plt.xlabel(self.X_label)
        plt.ylabel(self.Y_label)
        plt.title(self.title)
        plt.grid(self.show_grid)   
        plt.show()
            
        # End of user code	
    # Start of user code -> methods for Basegraph class

    # End of user code

