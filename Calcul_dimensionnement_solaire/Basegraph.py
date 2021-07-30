import matplotlib as mil
mil.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline 
class Basegraph(object):
    def __init__(self,x_values,y_values):
        self.Y_label = "Potentiel solaire"
        self.X_label = "Heures de l'année"
        self.show_grid = True
        self.title = "Potentiel solaire de la localisation sur une année"
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
        
        # End of user code	
    # Start of user code -> methods for Basegraph class

    # End of user code

