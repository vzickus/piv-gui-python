#piv-gui-pyhton
A python GUI for inspecting correlation matrices of Particle Image Velocimetry (PIV) analysis. This GUI currently uses correlation data format of OpenPIV (www.openpiv.net). The user is assumed to be familiar with pyhton OpenPIV.

#Warning
This GUI is still in the alpha stage - it's most likely buggy, and not all buttons are functional.

It's developed in Linux environment, but all the required dependencies are multi-platform (this GUI was tested on Linux/Mac/Win7.)

#Motivation
In essence, PIV relies on statistical "best match" approach, when estimating velocity vectors. While PIV is a well established method, outlier (incorrectly identified) vectors often show up in the calculated flow field. Inspecting correlation matrices can reveal the reason of an outlier vector. This GUI also enables the user to quickly change the Interogation Window size.

#Requirements
OpenPIV and its dependencies, as well as Qt, Sip, an PyQt.
Installation instruction for OpenPIV can be found here: http://openpiv.readthedocs.org/en/latest/src/installation_instruction.html
Installation instructions for Qt, Sip, and PyQt are widely available online, e.g. : http://doc.qt.io/qt-4.8/installation.html, http://pyqt.sourceforge.net/Docs/PyQt4/installation.html.

#Running
Once the repository is cloned, simply navigate to the folder where main_openpiv.py is and type 'python main_openpiv.py' in the terminal. This should hopefully start the GUI. Example data images are included in the repository. Below is a screenshot of the GUI in action. 
![](./piv_gui.png)
-Depending on your screen size, there might be 2 pairs of scroll bars appearing (if the image doesn't fit into in the allocated area, scroll bars appear). The outer scrollbars are for moving IWs.
-Sliding bar,and Prev./Next Frame buttons moves to the next/previous frame.
-Load button is currently not functional. This could be functionalized for image loading.
-Small/Big IW/overlap size spin boxes set the sizes of the windows/overlap assuming square IWs.
-Small/Big Iw are currently set to be scaled to 64x64, and 128x128 px size before displaying.
-Combobox is currently not functional. The plan is to incorporate "on demand" vector plotting, for either paired or sequential images.
-Redaraw IWs checkbox to either redraw or fix IWs when switching between frames.
-Plot correlation matrix button calls a pop-up window, which display the correlation matrix. The correlation matrix is fully rotatable.



#Contributors

Vytautas Zickus
Jonathan Taylor





