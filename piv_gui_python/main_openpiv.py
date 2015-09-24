#! usr/bin/env python

"""A basic GUI for inspecting PIV correlation matrices. PIV analysis functions here are based on/imported from OpenPIV www.openpiv.net
GUI developed by V.Zickus (v.zickus.1 at research.gla.ac.uk) with the help of Dr J.Taylor."""


import sys
from PyQt4 import QtGui, QtCore
from PIL import ImageQt
from scaler_gui import Ui_Form
import scipy.misc
import numpy as np
import glob
from windowclass import Window
import openpiv.process

class Main(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        #get the frames and sort them (need a leading zero). 
        ###TODO: functionalize the load button to choose the directory of the images/(type?).
        self.frames = sorted(glob.glob('./*.png'))
        self.raw_frames = sorted(glob.glob('./raw/*.bmp'))
        self.frame_size_x = scipy.misc.imread(self.frames[0]).shape[1]
        self.frame_size_y = scipy.misc.imread(self.frames[0]).shape[0]
        
        #set some default values. 
        ###TODO:These values should be automatically set to whatever IW/overlap sizes were set in the analysis.
        self.iw_small_size_value = 32
        self.iw_big_size_value = 64
        self.overlap_size_value = 48
        self.ui.iw_small_size.setValue(self.iw_small_size_value )
        self.ui.iw_big_size.setValue(self.iw_big_size_value)
        self.ui.iw_overlap_size.setValue(self.overlap_size_value )

        #set the maximum overlap value
        self.ui.iw_overlap_size.setMaximum(self.iw_big_size_value-1)
        self.subwindow_inset = (self.iw_big_size_value-self.iw_small_size_value)/2
        self.iw_pos_x_value = 0
        self.iw_pos_y_value = 0
        self.main_slider_value = 0
        
        #setup next/previous buttons
        self.ui.next_frame.clicked.connect(lambda: self.set_slider(+1))
        self.ui.prev_frame.clicked.connect(lambda: self.set_slider(-1))
        
        #setup main slider
        self.ui.main_slider_value.valueChanged.connect(self.main_slider_value_changed)
        self.ui.main_slider_value.setMaximum(len(self.frames)-1)
        
        #setup IW/overlap size input boxes
        self.ui.iw_small_size.valueChanged.connect(self.set_small_iw_size)
        self.ui.iw_big_size.valueChanged.connect(self.set_big_iw_size)
        self.ui.iw_overlap_size.valueChanged.connect(self.set_iw_overlap_size)
        
        #setup maximum values for iw sliders
        self.ui.iw_pos_x.setMaximum( (self.frame_size_x - self.iw_big_size_value)/self.iw_big_size_value )
        self.ui.iw_pos_y.setMaximum( (self.frame_size_y - self.iw_big_size_value )/self.iw_big_size_value )
        
        #setup iw sliders
        self.ui.iw_pos_x.valueChanged.connect(self.iw_pos_x_slider_value)
        self.ui.iw_pos_y.valueChanged.connect(self.iw_pos_y_slider_value)
        
        #setup redraw iws checkbox and its auxilary function
        self.ui.redraw_iws.stateChanged.connect(self.check_state)
        self.state = self.ui.redraw_iws.isChecked()
        
        #setup plot correlation matrix button
        self.ui.plot_corr_mat.clicked.connect(self.plot_corr_mat_btn_clicked)
        
        #set up the initial images on the GUI, so it would look better
        self.main_pixmap = QtGui.QPixmap(self.frames[0])
        self.draw_iw_bounds(self.main_pixmap)
        self.ui.label_main.setPixmap(self.main_pixmap)
        self.display_small_iw()
        self.display_big_iw()
        
        #reference image for getting intensity values...
        self.main_pixmap_ref_array = scipy.misc.imread((self.raw_frames[0]))
        
        #update iw slider max
        self.update_iw_slider_max()
        
        #Sets up mouse action on main window (not tested with scaling...)
        self.ui.label_main.mousePressEvent = self.getPos  
        

    #######################
    #GUI specific functions
    #######################
    
    def getPos(self , event):
        """Prints the position of the mouse click and corresponding intensity value on the main image. The print out happens in the console"""
        x = event.pos().x()
        y = event.pos().y()
        c = self.main_pixmap_ref_array[y][x]
        print 'x,y,int =',x,y,c    
        
    def set_slider(self,delta):
        """Changes the main frame slider by singleStep value when next/prev buttons are clicked."""
        self.ui.main_slider_value.setValue(self.ui.main_slider_value.value() + delta * self.ui.main_slider_value.singleStep())
    
    def update_iw_slider_max(self):
        """Enables the sliders to be 'draged by mouse' and to match the IW positions."""
        #It seems that there is no nice and simple way to be able to use "mouse sliding" of sliders so that the values would not move at arbitrary points, but to exact IW positions. One workaround is to set the maximum value of the slider to the one divided by the big IW size. However, we must take into account that we might have an overlap. This means quite a long expression, but the code could probably be cleaned up a bit by setting the "self.iw_big_size_value - self.overlap_size_value" to a single instance variable at init. It gets particularly messy in display_small/big_iw functions...
        self.ui.iw_pos_x.setMaximum( (scipy.misc.imread(self.frames[0]).shape[1] - self.iw_big_size_value )/(self.iw_big_size_value - self.overlap_size_value ) )
        self.ui.iw_pos_y.setMaximum( (scipy.misc.imread(self.frames[0]).shape[0] - self.iw_big_size_value )/(self.iw_big_size_value - self.overlap_size_value ) )
        
    def update_overlap_max(self):
        """Updates the big IW overlap size."""
        #We should not allow the overlap value to exceed the big IW value, as that will result in an error
        self.ui.iw_overlap_size.setMaximum(self.iw_big_size_value-1)
        
    def update_subwindow_inset(self):
        """Updates the subwindow inset"""
        self.subwindow_inset = (self.iw_big_size_value-self.iw_small_size_value)/2
                
    def set_small_iw_size(self, value):             
        """Takes the input value for the small IW size from the gui and sets it as an instance variable."""
        self.iw_small_size_value = value
        #the gui should only allow integers, but just in case we have an assertion.
        assert isinstance(value, int)
        self.update_subwindow_inset()
        self.display_main_image()
        
    def set_big_iw_size(self, value):
        """Takes the input value for the big IW size from the gui and sets it as an instance variable."""
        self.iw_big_size_value = value
        assert isinstance(value, int)
        self.display_main_image()
        self.update_subwindow_inset()
        self.update_iw_slider_max()
        self.update_overlap_max()
        
    def set_iw_overlap_size(self, value):
        """Takes the input value for the big IW overlap size from the gui and sets it as an instance variable."""
        self.overlap_size_value = value
        assert isinstance(value, int)
        self.display_main_image()
        self.update_iw_slider_max()
        
    def iw_pos_x_slider_value(self,value):
        """Functionality triggered by moving horizontal iw slider"""
        self.iw_pos_x_value = value*(self.iw_big_size_value - self.overlap_size_value)
        assert isinstance(value, int)
        self.display_main_image()
        self.display_small_iw()
        self.display_big_iw()
        
    def iw_pos_y_slider_value(self,value):
        """Functionality trigerred by moving vertical iw slider"""
        self.iw_pos_y_value = value*(self.iw_big_size_value - self.overlap_size_value)
        assert isinstance(value, int)
        self.display_main_image()
        self.display_small_iw()
        self.display_big_iw()
        
    def main_slider_value_changed(self,new_value):
        """Gets the main slider value and draws the main image"""   
        self.main_slider_value = new_value
        assert isinstance(new_value, int)
        self.display_main_image()
    
    
    def display_main_image(self):
        """Displays the main image."""
        self.main_pixmap = QtGui.QPixmap(self.frames[self.main_slider_value])
        #Reference image updated...
        self.main_pixmap_ref_array = scipy.misc.imread(self.raw_frames[self.main_slider_value])
        #Draws IW bounds
        self.draw_iw_bounds(self.main_pixmap)
        ####TODO: scale the whole thing. see http://stackoverflow.com/questions/24106903/resizing-qpixmap-while-maintaining-aspect-ratio, http://stackoverflow.com/questions/21041941/how-to-autoresize-qlabel-pixmap-keeping-ratio-without-using-classes
        ####TODO: enable zooming
        self.ui.label_main.setPixmap(self.main_pixmap)    
        #Updates the IW images if necessary.
        self.replot_iws()
        
    def draw_iw_bounds(self,main_pixmap):
        """Draws the rectangles of IW window sizes on the main image. The centre is indicated by a green dot."""
        
        draw = QtGui.QPainter(self.main_pixmap)
        draw.setBrush(QtCore.Qt.NoBrush)
        draw.setPen(QtCore.Qt.blue)
        #Draw the small IW centered on the big IW.drawRect takes (x,y, width, height). Check what happens if the value is NOT divisible by 2.
        draw.drawRect(self.iw_pos_x_value + (self.iw_big_size_value - self.iw_small_size_value)/2, self.iw_pos_y_value + (self.iw_big_size_value - self.iw_small_size_value)/2, self.iw_small_size_value,self.iw_small_size_value )
        draw.setPen(QtCore.Qt.red)
        #Draw the big IW
        draw.drawRect(self.iw_pos_x_value, self.iw_pos_y_value, self.iw_big_size_value, self.iw_big_size_value)
        draw.setPen(QtCore.Qt.green)
        #Draw a point in the centre of the two IWs.
        draw.drawPoint(self.iw_big_size_value/2 + self.iw_pos_x_value, self.iw_big_size_value/2 + self.iw_pos_y_value)    

    def display_small_iw(self):    
        """Displays the small IW. Uses an extension of moving_window_array function from openpiv.The frame from which small_IWs are obtained are called frame_a or "first" frame, since we assume positive time change and frame_a is compared to frame_b. So in positive time change, and appropriate flow conditions, the big_iw should preserve the information from small_iw, hence minimising in-plane information loss."""
        
        frame_a = scipy.misc.imread(self.raw_frames[self.main_slider_value])
        self.small_windows = self.moving_sub_window_array(frame_a, self.iw_big_size_value, self.overlap_size_value, self.subwindow_inset)
        
        #field shape provides the information how many big IWs fit in the frame of interest.
        self.field_shape = openpiv.process.get_field_shape(image_size = scipy.misc.imread(self.raw_frames[self.main_slider_value]).shape, window_size = self.iw_big_size_value, overlap = self.overlap_size_value)
        
        ###TODO: try and make this more readable. Automate scaling?
        self.pixmap_small_iw = QtGui.QPixmap.fromImage(ImageQt.ImageQt(scipy.misc.toimage(self.small_windows[self.iw_pos_x_value/(self.iw_big_size_value - self.overlap_size_value) + (self.iw_pos_y_value/(self.iw_big_size_value- self.overlap_size_value))*self.field_shape[1]], cmax = 255, cmin = 0))).scaled(64, 64, QtCore.Qt.KeepAspectRatio)
        self.ui.label_small_iw.setPixmap(self.pixmap_small_iw)
        
      
    def display_big_iw(self):   
        """Displays the big IW. Uses modified moving_window_array function from openpiv.The frame from which big_IWs are obtained are called frame_b or "second" frame, since we assume positive time change and frame_a is compared to frame_b."""
        
        ###TODO: make sure this is consistent with openpiv correlation.
        frame_b = scipy.misc.imread(self.raw_frames[self.main_slider_value + 1])
        self.big_windows = self.moving_window_array(frame_b, self.iw_big_size_value, self.overlap_size_value)
        
        ###TODO: try and make this more readable. Automate scaling?
        self.pixmap_big_iw = QtGui.QPixmap.fromImage(ImageQt.ImageQt(scipy.misc.toimage(self.big_windows[self.iw_pos_x_value/(self.iw_big_size_value - self.overlap_size_value) + (self.iw_pos_y_value/(self.iw_big_size_value- self.overlap_size_value))*self.field_shape[1]], cmax = 255, cmin = 0))).scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        
        ###TODO: need to find a way how to set a vmin,vmax for the images, so the scale of the small_iw and big_iw would be the same...
        self.ui.label_big_iw.setPixmap(self.pixmap_big_iw)        
        
    def check_state(self,state):
        """Calls replot_iws when checkbox state is changed so that IW's would get updated without changing the frame/IW position"""
        self.replot_iws()    
    
    def replot_iws(self):
        """Sometimes it might be useful to redraw the IWs from previous frame matching, for instance, is there is a need to switch between two main frames, to see the "big picture" flow. """
        
        self.state = self.ui.redraw_iws.isChecked()
        if self.state == True:
            self.display_small_iw()
            self.display_big_iw()
        else:
            pass

    def plot_corr_mat_btn_clicked(self):
        """This function calls a pop up window which shows the correlation matrix"""
        
        calc_cor_matrix = openpiv.process.correlate_windows( window_a = self.small_windows[self.iw_pos_x_value/(self.iw_big_size_value - self.overlap_size_value) + (self.iw_pos_y_value/(self.iw_big_size_value- self.overlap_size_value))*self.field_shape[1]].astype(np.float64), window_b = self.big_windows[self.iw_pos_x_value/(self.iw_big_size_value - self.overlap_size_value) + (self.iw_pos_y_value/(self.iw_big_size_value- self.overlap_size_value))*self.field_shape[1]].astype(np.float64), corr_method = 'fft', nfftx = None, nffty = None )

        self.corr_mat_plt = Window(calc_cor_matrix.shape[0],calc_cor_matrix.shape[1],calc_cor_matrix, self.main_slider_value)
        self.corr_mat_plt.show()
        
        
    #################
    #Helper functions
    #################
    
    def moving_window_array(self, array, window_size, overlap):
        """Returns what the original openpiv moving_window_array function did."""
        return self.moving_sub_window_array(array, window_size, overlap, 0)

    def moving_sub_window_array( self, array, window_size, overlap, subwindow_inset ):
        """
        Parameters
        ----------
        array = 3D image array that we want to access in terms of its IWs

        window_size = size of each large IW

        overlap = overlap between adjacent large IWs

        subwindow_inset = the size of how far away from the boundary we push the centre of the smaller window (similar to cropping).
                            This can be set to 0 if we want to obtain the array used to access the large IW.
                            
        Written by Dr Jonathan Taylor. Based on moving_window_array function in OpenPIV (www.openpiv.net).
        """
        # The implementation of this function is rather complicated, involving the use of numpy's stride_tricks library.
        # The intention is to provide a 3D array that can be indexed using the parameters: IW index, x coord within IW, y coord within IW.
        # In order to achieve this we create a 4D array (IW x index, IW y index, ...), and flatten the first two dimensions into one.
        # Creating a 4D array like this is "relatively" easy using stride_tricks in the case where the first IW starts at (0,0).
        # However, things get a little harder if we want to create an array of small IWs, since these are inset and hence do not start at (0,0).
        # They start at (subwindow_inset, subwindow_inset). In order to achieve that we actually need to create a *fifth* dimension to
        # our intermediate array, with a stride that takes us from (0,0) to the correct starting point. We then pick out the second
        # array element in that dimension, which gives us what we want.
        sz = array.itemsize
        shape = array.shape
        subwindow_size = window_size - 2*subwindow_inset
        assert(subwindow_size > 0)
        strides = (sz*(shape[1]*subwindow_inset+subwindow_inset), sz*shape[1]*(window_size-overlap), sz*(window_size-overlap), sz*shape[1], sz)
        shape = (2, int((shape[0] - window_size)/(window_size-overlap))+1, int((shape[1] - window_size)/(window_size-overlap))+1 , subwindow_size, subwindow_size)
        return np.lib.stride_tricks.as_strided( array, strides=strides, shape=shape )[1,:,:,:,:].reshape(-1, subwindow_size, subwindow_size)
    
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle('cleanlooks')
    window = Main()
    window.show()
    sys.exit(app.exec_())
