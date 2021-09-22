import matplotlib as mil
mil.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline 
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
        
        # End of user code	
    # Start of user code -> methods for Basegraph class

    # End of user code

