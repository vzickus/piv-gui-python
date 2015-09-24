from PyQt4 import QtGui
 
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d



class Window(QtGui.QDialog):
    def __init__(self, shape_0, shape_1, corr_mat, frame_number, parent=None):
        super(Window, self).__init__(parent)
        
        self.frame_number = frame_number
        self.corr_mat = corr_mat
        self.shape_0 = shape_0
        self.shape_1 = shape_1

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.plot()
        
        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        

    def plot(self):
        
        data = self.corr_mat
        self.ax = Axes3D(self.figure)
        self.nx, self.ny = self.shape_0,self.shape_1
        self.xx = range(self.nx)
        self.yy = range(self.ny)  
        xmax = np.argmax(np.max(data, axis=0))
        ymax = np.argmax(np.max(data, axis=1))        
        self.ax.set_xlabel('x axis. Peak column = ' +str(xmax))
        self.ax.set_ylabel('y axis. Peak row = ' + str(ymax))
        self.ax.set_title('Frame ' + str(self.frame_number))
        self.X, self.Y = np.meshgrid(self.xx, self.yy)
        self.ax.plot_surface(self.X , self.Y , data , rstride = 1, cstride = 1,alpha=0.7)
        #TODO: Countours are sometimes not plotted properly. Investigate this.
        cset = self.ax.contour(self.X, self.Y, data, zdir='z', offset=0, cmap=cm.coolwarm)
        cset = self.ax.contour(self.X, self.Y, data, zdir='x', offset=0, cmap=cm.coolwarm)
        cset = self.ax.contour(self.X, self.Y, data, zdir='y', offset=self.shape_0, cmap=cm.coolwarm)
        
        #TODO: Need to make the ticks appear in a reasonable way. Sometimes too dense.
        self.ax.set_xticks(np.arange(0,self.shape_1,4))
        self.ax.set_yticks(np.arange(0,self.shape_1,4))

        self.canvas.draw()
        ###TODO: Show the mask, show the contours. Show "snr" ?
