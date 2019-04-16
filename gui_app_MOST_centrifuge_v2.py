'''***********************************************************************************************
*                                                                                                *
*                       Open Source Completely 3D Printable Centrifuge                           *
*                Salil S. Sule, Aliaksei L. Petsiuk and Joshua M. Pearce                         *
*                                                                                                *
*                     Michigan Tech Open Sustainability Technology Lab                           * 
*                                        April 2019                                              *
*                                                                                                *
*                                                                                                *
* A camera-based GUI application to validate the rotational speed of the open source 3D          *
* printable centrifuge.                                                                          *                                                                      * 
*                                                                                                *
* © 2019 by the authors. Submitted for possible open access publication under the terms          *
* and conditions of the Creative Commons Attribution (CC BY) license                             *
* (http://creativecommons.org/licenses/by/4.0/)                                                  *
                                                                                                 *
***********************************************************************************************'''

#!/usr/bin/env python

# ------------------- REQUIRED MODULES ------------------
import sys
import cv2
import time
import numpy as np
import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QComboBox, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib import colors as mcolors

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


#-------------------------- WIDGET ----------------------------
class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Centrifuge::Spin Counter'
        self.left = 100
        self.top = 100
        self.width = 1200
        self.height = 680
        self.initUI()
 
    def initUI(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.lbl_BIG_RPM = QtWidgets.QLabel('RPM')
        self.lbl_BIG_RPM.setAlignment(Qt.AlignRight)
        self.lbl_BIG_RPM.setStyleSheet("QLabel {color: #708090;}")
        self.lbl_BIG_RPM.setFont(QtGui.QFont('Sans',18,QtGui.QFont.Bold))

        self.lbl_BIG_RCF = QtWidgets.QLabel('RCF')
        self.lbl_BIG_RCF.setAlignment(Qt.AlignRight)
        self.lbl_BIG_RCF.setStyleSheet("QLabel {color: #C0C0C0;}")
        self.lbl_BIG_RCF.setFont(QtGui.QFont('Sans',18,QtGui.QFont.Bold))

        self.btn_CAM = QtWidgets.QPushButton('Open CAM')
        self.btn_OPEN_VID = QtWidgets.QPushButton('Open Video')

        self.lbl_CENTR_PARAMS = QtWidgets.QLabel('Set centrifuge parameters')
        self.lbl_CENTR_PARAMS.setAlignment(Qt.AlignLeft)
        self.lbl_CENTR_PARAMS.setStyleSheet("QLabel {background-color: #C0C0C0; color: #666666;}")
        self.lbl_CENTR_PARAMS.setFont(QtGui.QFont('Sans',11,QtGui.QFont.Bold))

        self.lbl_CROP_ROI = QtWidgets.QLabel('Crop the region of interest')
        self.lbl_CROP_ROI.setAlignment(Qt.AlignLeft)
        self.lbl_CROP_ROI.setStyleSheet("QLabel {background-color: #C0C0C0; color: #666666;}")
        self.lbl_CROP_ROI.setFont(QtGui.QFont('Sans',11,QtGui.QFont.Bold))

        self.lbl_RGB_THRESH = QtWidgets.QLabel('Set RGB thresholds')
        self.lbl_RGB_THRESH.setAlignment(Qt.AlignLeft)
        self.lbl_RGB_THRESH.setStyleSheet("QLabel {background-color: #C0C0C0; color: #666666;}")
        self.lbl_RGB_THRESH.setFont(QtGui.QFont('Sans',11,QtGui.QFont.Bold))

        self.btn_SET_ROI = QtWidgets.QPushButton('SET VALUES AND CROP')
        self.btn_SET_ROI.setStyleSheet("QPushButton {background-color: #6495ED;}")

        self.btn_TRACE_MARKERS = QtWidgets.QPushButton('TRACE MARKERS')
        self.btn_TRACE_MARKERS.setStyleSheet("QPushButton {background-color: #6495ED;}")
        self.btn_SET_GEAR_RATIO = QtWidgets.QPushButton('  Set Gear Ratio  ')
        self.textbox_GEAR_RATIO = QtWidgets.QLineEdit()
        self.btn_SET_TUBE_LENGTH_D = QtWidgets.QPushButton('Set Tube Length')
        self.textbox_TUBE_LENGTH_D = QtWidgets.QLineEdit()
        self.btn_COMPUTE_VELOCITY = QtWidgets.QPushButton('PLOT RPM AND RCF')
        self.btn_COMPUTE_VELOCITY.setStyleSheet("QPushButton {background-color: #6495ED;}")

        self.textbox_CROP_X = QtWidgets.QLineEdit('Start X')
        self.textbox_CROP_Y = QtWidgets.QLineEdit('Start Y')
        self.textbox_CROP_WIDTH = QtWidgets.QLineEdit('Crop width')
        self.textbox_CROP_LENGTH = QtWidgets.QLineEdit('Crop length')

        self.btn_RCF_OF_RPM = QtWidgets.QPushButton('PLOT RCF(RPM) FUNCTION')
        self.btn_RESET_TIMER = QtWidgets.QPushButton('Reset Timer')

        self.lbl_TIMER = QtWidgets.QLabel('Spinning Time: ')
        self.lbl_TIMER_seconds = QtWidgets.QLabel('')
        self.lbl_TIMER_seconds.setStyleSheet("QLabel {color: #666666;}")
        self.lbl_TIMER_seconds.setFont(QtGui.QFont('Sans',12,QtGui.QFont.Bold))
        self.lbl_TIMER_seconds.setAlignment(Qt.AlignCenter)

        self.lbl_CROP = QtWidgets.QLabel('X')
        self.lbl_CROP.setStyleSheet("QLabel {background-color: #000000; color: #FFFFFF;}")
        self.lbl_CROP.setFont(QtGui.QFont('Sans',10,QtGui.QFont.Bold))


        self.lbl_color_channel_1 = QtWidgets.QLabel('R')
        self.lbl_color_channel_1.setStyleSheet("QLabel {background-color: #EE7070;}")
        self.lbl_color_channel_1.setFont(QtGui.QFont('Sans',10,QtGui.QFont.Bold))

        self.lbl_color_channel_2 = QtWidgets.QLabel('G')
        self.lbl_color_channel_2.setStyleSheet("QLabel {background-color: #70EE70;}")
        self.lbl_color_channel_2.setFont(QtGui.QFont('Sans',10,QtGui.QFont.Bold))

        self.lbl_color_channel_3 = QtWidgets.QLabel('B')
        self.lbl_color_channel_3.setStyleSheet("QLabel {background-color: #7070EE;}")
        self.lbl_color_channel_3.setFont(QtGui.QFont('Sans',10,QtGui.QFont.Bold))

        #------------------------------------------------------
        dynamic_canvas = FigureCanvas(Figure(figsize=(8, 2)))
        #self.addToolBar(QtCore.Qt.BottomToolBarArea,NavigationToolbar(dynamic_canvas, self))
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self.color = 'tab:grey'
        self._dynamic_ax.set_xlabel('Time, s')
        self._dynamic_ax.set_ylabel('Radial Velocity, rad/s',color=self.color)
        self._dynamic_ax.tick_params(axis='y',labelcolor=self.color)
        self.color = 'tab:blue'
        # uncomment the lines below in case if you need a second axis
        self._dynamic_ax2 = self._dynamic_ax.twinx() # use the same x-axis for the self._dynamic_ax2
        self._dynamic_ax2.set_ylabel('Relative Centrifugal Force, N',color=self.color)
        self._dynamic_ax2.tick_params(axis='y',labelcolor=self.color)
        self._timer = dynamic_canvas.new_timer(100, [(self._update_canvas, (), {})])
        self._timer.start()
        t = np.linspace(0, 100, 120)
        #------------------------------------------------------
        
        self.btn_matplotlib = QtWidgets.QPushButton('3D Fused Plot')
        self.lbl_support = QtWidgets.QLabel('Technical Support: apetsiuk@mtu.edu')
        self.lbl_support.setAlignment(Qt.AlignRight)
        self.lbl_support.setFont(QtGui.QFont('Sans',9,QtGui.QFont.Light))
		
        self.lbl_logo = QtWidgets.QLabel()
        self.lbl_blank_space = QtWidgets.QLabel()
        self.lbl_logo.setPixmap(QtGui.QPixmap('images/most_centrifuge_logo.png'))
       
        #--------------------- RGB SLIDERS---------------------
        self.slider_R_lower = QSlider(Qt.Horizontal)
        self.slider_R_lower.setFocusPolicy(Qt.StrongFocus)
        self.slider_R_lower.setTickPosition(QSlider.TicksAbove)
        self.slider_R_lower.setTickInterval(4)
        self.slider_R_lower.setSingleStep(2)

        self.slider_R_upper = QSlider(Qt.Horizontal)
        self.slider_R_upper.setFocusPolicy(Qt.StrongFocus)
        self.slider_R_upper.setTickPosition(QSlider.TicksAbove)
        self.slider_R_upper.setTickInterval(4)
        self.slider_R_upper.setSingleStep(2)

        self.slider_G_lower = QSlider(Qt.Horizontal)
        self.slider_G_lower.setFocusPolicy(Qt.StrongFocus)
        self.slider_G_lower.setTickPosition(QSlider.TicksAbove)
        self.slider_G_lower.setTickInterval(4)
        self.slider_G_lower.setSingleStep(2)

        self.slider_G_upper = QSlider(Qt.Horizontal)
        self.slider_G_upper.setFocusPolicy(Qt.StrongFocus)
        self.slider_G_upper.setTickPosition(QSlider.TicksAbove)
        self.slider_G_upper.setTickInterval(4)
        self.slider_G_upper.setSingleStep(2)

        self.slider_B_lower = QSlider(Qt.Horizontal)
        self.slider_B_lower.setFocusPolicy(Qt.StrongFocus)
        self.slider_B_lower.setTickPosition(QSlider.TicksAbove)
        self.slider_B_lower.setTickInterval(4)
        self.slider_B_lower.setSingleStep(2)

        self.slider_B_upper = QSlider(Qt.Horizontal)
        self.slider_B_upper.setFocusPolicy(Qt.StrongFocus)
        self.slider_B_upper.setTickPosition(QSlider.TicksAbove)
        self.slider_B_upper.setTickInterval(4)
        self.slider_B_upper.setSingleStep(2)
        

        #---------------------------- LAYOUT --------------------------		
        layout_H = QtWidgets.QHBoxLayout()
        layout_H_LOGO = QtWidgets.QHBoxLayout()
        layout_H_X = QtWidgets.QHBoxLayout() # for crop
        layout_H_R = QtWidgets.QHBoxLayout()
        layout_H_G = QtWidgets.QHBoxLayout()
        layout_H_B = QtWidgets.QHBoxLayout()
        layout_H_CAM = QtWidgets.QHBoxLayout()

        layout_H_GEARS = QtWidgets.QHBoxLayout()
        layout_H_TUBES = QtWidgets.QHBoxLayout()
        layout_H_TIMER = QtWidgets.QHBoxLayout()

        layout_V = QtWidgets.QVBoxLayout()
        layout_V2 = QtWidgets.QVBoxLayout()
        layout_V3 = QtWidgets.QVBoxLayout()
        layout_V_RPM_RCF = QtWidgets.QVBoxLayout()
        

        #------------------------- 1ST COLUMN--------------------------
        layout_H_LOGO.addWidget(self.lbl_logo)
        layout_V_RPM_RCF.addWidget(self.lbl_BIG_RPM)
        layout_V_RPM_RCF.addWidget(self.lbl_BIG_RCF)
        layout_V_RPM_RCF.addWidget(self.lbl_blank_space)
        layout_V_RPM_RCF.addWidget(self.lbl_blank_space)
        layout_H_LOGO.addLayout(layout_V_RPM_RCF)
        layout_V.addLayout(layout_H_LOGO)

        layout_V.addWidget(self.lbl_CENTR_PARAMS)

        layout_H_TUBES.addWidget(self.btn_SET_GEAR_RATIO)
        layout_H_TUBES.addWidget(self.textbox_GEAR_RATIO)
        layout_H_TUBES.addWidget(self.btn_SET_TUBE_LENGTH_D)
        layout_H_TUBES.addWidget(self.textbox_TUBE_LENGTH_D)
        layout_V.addLayout(layout_H_TUBES)
        layout_H_CAM.addWidget(self.btn_CAM)
        layout_H_CAM.addWidget(self.btn_OPEN_VID)
        layout_V.addLayout(layout_H_CAM)

        layout_V.addWidget(self.lbl_blank_space)
        layout_V.addWidget(self.lbl_CROP_ROI)

        layout_H_X.addWidget(self.lbl_CROP)
        layout_H_X.addWidget(self.textbox_CROP_X)
        layout_H_X.addWidget(self.textbox_CROP_Y)
        layout_H_X.addWidget(self.lbl_blank_space)
        layout_H_X.addWidget(self.textbox_CROP_WIDTH)
        layout_H_X.addWidget(self.textbox_CROP_LENGTH)
        layout_V.addLayout(layout_H_X)
        layout_V.addWidget(self.btn_SET_ROI)

        layout_V.addWidget(self.lbl_blank_space)
        layout_V.addWidget(self.lbl_RGB_THRESH)
        layout_H_R.addWidget(self.lbl_color_channel_1)
        layout_H_R.addWidget(self.slider_R_lower)
        layout_H_R.addWidget(self.lbl_blank_space)
        layout_H_R.addWidget(self.slider_R_upper)
        layout_V.addLayout(layout_H_R)

        layout_H_G.addWidget(self.lbl_color_channel_2)
        layout_H_G.addWidget(self.slider_G_lower)
        layout_H_G.addWidget(self.lbl_blank_space)
        layout_H_G.addWidget(self.slider_G_upper)
        layout_V.addLayout(layout_H_G)

        layout_H_B.addWidget(self.lbl_color_channel_3)
        layout_H_B.addWidget(self.slider_B_lower)
        layout_H_B.addWidget(self.lbl_blank_space)
        layout_H_B.addWidget(self.slider_B_upper)
        layout_V.addLayout(layout_H_B)

        layout_V.addWidget(self.btn_TRACE_MARKERS)
        #layout_V.addWidget(self.lbl_blank_space)

        layout_V.addWidget(self.btn_RCF_OF_RPM)

        layout_H_TIMER.addWidget(self.btn_RESET_TIMER)
        layout_H_TIMER.addWidget(self.lbl_TIMER_seconds)
        layout_V.addLayout(layout_H_TIMER)
        
        layout_H.addLayout(layout_V)
        
        #------------------------- 2ND COLUMN -------------------------
        layout_V2.addWidget(dynamic_canvas)
        layout_H.addLayout(layout_V2)
        
        #------------------------- COMBINED ---------------------------
        layout_V3.addLayout(layout_H)
        self.setLayout(layout_V3)
		
        #------------------------ CONNECTIONS -------------------------
        self.btn_CAM.clicked.connect(self.btn_CAM_0_click_function)
        self.btn_OPEN_VID.clicked.connect(self.btn_OPEN_VID_click_function)
        self.slider_R_lower.valueChanged.connect(self.slider_R_lower_change)
        self.slider_R_upper.valueChanged.connect(self.slider_R_upper_change)
        self.slider_G_lower.valueChanged.connect(self.slider_G_lower_change)
        self.slider_G_upper.valueChanged.connect(self.slider_G_upper_change)
        self.slider_B_lower.valueChanged.connect(self.slider_B_lower_change)
        self.slider_B_upper.valueChanged.connect(self.slider_B_upper_change)
        self.btn_SET_GEAR_RATIO.clicked.connect(self.btn_SET_GEAR_RATIO_clicked)
        self.btn_RESET_TIMER.clicked.connect(self.btn_RESET_TIMER_function)
        self.btn_TRACE_MARKERS.clicked.connect(self.btn_TRACE_MARKERS_function)
        self.btn_SET_ROI.clicked.connect(self.btn_SET_ROI_function)
        self.btn_RCF_OF_RPM.clicked.connect(self.btn_RCF_OF_RPM_function)

        self.show()
		
    #------------------------ VARIABLES -------------------------
    slider_R_lower_value = 0 # defaults
    slider_G_lower_value = 12
    slider_B_lower_value = 62

    slider_R_upper_value = 44
    slider_G_upper_value = 100
    slider_B_upper_value = 100

    Crop_X_Start = 0 # defaults
    Crop_Y_Start = 0
    Crop_Width   = 800
    Crop_Height  = 600

    gear_ratio  = 10
    tube_length = 15

    
    spin_time = time.time() # for app timer
    start_timer = 0 # for frame timer
    trace_markers_FLAG = 0 # button is not pressed
    
    azimuth = 0
    rpm = 0
    rcf = 0
    rotations = 0
    count = 0
    prev_count = 0
    previous_time = 0

    graph_x_size = 120
    graph_step = 0
    rpm2=np.zeros(graph_x_size) # to plot the graph
    rcf2=np.zeros(graph_x_size) # to plot the graph

    font = cv2.FONT_HERSHEY_SIMPLEX


    #------------------------ FUNCTIONS -------------------------

    def btn_CAM_0_click_function(self):
        cap = cv2.VideoCapture(0)
        #cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

        # check if camera opened successfully
        if (cap.isOpened()== False): 
            print("Error opening video stream or file")
 
        # get frame resolution
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
 
        # define the codec and create VideoWriter object.The output is stored in 'out_cam_processed.avi' file.
        out = cv2.VideoWriter('video_out.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))

        while(cap.isOpened()):
            ret, frame = cap.read()
            
            if ret==True:
                crop = frame[self.Crop_X_Start:self.Crop_X_Start+self.Crop_Width, self.Crop_Y_Start:self.Crop_Y_Start+self.Crop_Height]
                blur = cv2.blur(crop,(5,5))
                # find the traveler
                lowerB=np.array([int(self.slider_B_lower_value*2.55),int(self.slider_G_lower_value*2.55),int(self.slider_R_lower_value*2.55)])
                upperB=np.array([int(self.slider_B_upper_value*2.55),int(self.slider_G_upper_value*2.55),int(self.slider_R_upper_value*2.55)])
                maskB=cv2.inRange(blur,lowerB,upperB)
                # opening and closing
                kernelOpen=np.ones((5,5))
                kernelClose=np.ones((15,15))

                maskOpenB=cv2.morphologyEx(maskB,cv2.MORPH_OPEN,kernelOpen)
                maskCloseB=cv2.morphologyEx(maskOpenB,cv2.MORPH_CLOSE,kernelClose)
                maskCloseB_rgb = cv2.cvtColor(maskCloseB, cv2.COLOR_GRAY2BGR)

                # create transparent mask
                overlay = crop.copy()
                output = crop.copy()
                cv2.addWeighted(maskCloseB_rgb, 0.4, output, 1-0.4,0, output)

                # origin
                cxo = 350
                cyo = 309

                if self.trace_markers_FLAG == 1:
                    self.start_timer = time.time()
                    # traveler
                    im2b,contsb,hb=cv2.findContours(maskCloseB.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

                    if np.shape(contsb)[0] == 1:
                        cntB = contsb[0]
                        Mb = cv2.moments(cntB)
                        cxb = int(Mb['m10']/Mb['m00'])+self.Crop_X_Start
                        cyb = int(Mb['m01']/Mb['m00'])+self.Crop_Y_Start
                        cv2.putText(output,("Angle       = {:.2f}".format(self.azimuth*180/np.pi)),(400,100),self.font,1,(255,255,255),2,cv2.LINE_AA)
                        #cv2.putText(output,("Timer  = {:.2f}".format(time.time()-self.start_timer)),(20,100),self.font,0.8,(255,255,255),2,cv2.LINE_AA)
                        cv2.putText(output,("Revolutions = {:.0f}".format(self.rotations)),(400,150),self.font,1,(255,255,255),2,cv2.LINE_AA)
                        cv2.putText(output,("Tubes RPM = {:.2f}".format(self.rpm)),(400,200),self.font,1,(255,255,255),2,cv2.LINE_AA)
                        cv2.putText(output,("Tubes RCF  = {:.2f}".format(1.118*15*(self.rpm**2)*1e-6)),(400,250),self.font,1,(255,255,255),2,cv2.LINE_AA)
                    else:
                        cxb = cxo
                        cyb = cxo
                        cv2.putText(output,'Marker has been lost',(200,250),self.font,1,(0,0,255),2,cv2.LINE_AA)


                    cv2.circle(output,(cxo,cyo),10,(0,255,0),-1)
                    cv2.circle(output,(cxb,cyb),10,(255,250,0),-1)

                    # radius
                    cv2.line(output,(cxo,cyo),(cxb,cyb),(0,255,0),3)
                    radius = int(np.sqrt((np.absolute(cxb-cxo))**2+(np.absolute(cyb-cyo))**2))

                    # circumference
                    cv2.circle(output,(cxo,cyo),10,(0,255,255),-1)
                    cv2.circle(output,(cxo,cyo),radius,(0,255,0),2)

                    # azimuth
                    cv2.arrowedLine(output,(cxo,cyo),(cxo,cyo-50),(255,255,255),2)

                    # calculate azimuth
                    #self.azimuth = np.arcsin((cxb-cxo)/radius)
                    if cxb==cxo or cyb==cyo:
                        pass
                    elif cxb<cxo and cyb<cyo:
                        self.azimuth=np.arcsin((cxo-cxb)/radius)
                    elif cxb<cxo and cyb>cyo:
                        self.azimuth=np.arcsin((cxo-cxb)/radius)+np.pi/2
                    elif cxb>cxo and cyb>cyo:
                        self.azimuth=np.arcsin((cxb-cxo)/radius)+np.pi
                    elif cxb>cxo and cyb<cyo:
                        self.azimuth=np.arcsin((cxb-cxo)/radius)+np.pi*3/2

                    # calculate RPM (values 0.85 and 9 have been calibrated experimentally)
                    if np.round(self.azimuth,2) <= 0.85 and (self.count-self.prev_count)>9:
                        self.count=0
                        self.rpm = 60*self.gear_ratio/(time.time()-self.previous_time)
                        self.rcf = 1.118*self.tube_length*self.rpm**2*1e-6
                        self.previous_time = time.time()
                        self.rotations = self.rotations+1
                        self.prev_count = self.count
                        self.rpm2[self.rotations] = self.rpm # goes to plot
                        self.rcf2[self.rotations] = self.rcf # goes to plot

                        if self.rotations >= self.graph_x_size:
                            self.rotations = 0
                            self._dynamic_ax.clear()
                            self.rpm2=np.zeros(self.graph_x_size)
                            self.rcf2=np.zeros(self.graph_x_size)

                        self.rpm2[self.rotations] = self.rpm # goes to plot
                        self.rcf2[self.rotations] = self.rcf # goes to plot
                    
                    self.count = self.count+1
                #-----------------------------end of trace_markers_FLAG-----------------------------------------------------

                cv2.putText(output,"MTU MOST Centrifuge CAM",(20,30),self.font,1,(55,255,255),2,cv2.LINE_AA)  
                cv2.putText(output,("Timer  = {:.2f}".format(time.time()-self.start_timer)),(400,550),self.font,1,(255,255,255),2,cv2.LINE_AA) 
                
                # write a video file
                #out.write(output) 
                # display the output frame
                cv2.imshow("MTU MOST Centrifuge", output)  
           
                # Press Q on keyboard to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # release the video capture object and close all frames
                    cap.release()
                    cv2.destroyAllWindows()
                    break
            else:
                break
#-----------------------end of btn_CAM_0_click_function------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------------------------------
    def btn_OPEN_VID_click_function(self):
        cap = cv2.VideoCapture('video/calibrate_4.avi')
        #cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

        # check if camera opened successfully
        if (cap.isOpened()== False): 
            print("Error opening video stream or file")
 
        # get frame resolution
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
 
        # define the codec and create VideoWriter object.The output is stored in 'out_cam_processed.avi' file.
        #out = cv2.VideoWriter('out_vid_processed.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))

        while(cap.isOpened()):
            ret, frame = cap.read()
            
            if ret==True:
                crop = frame[self.Crop_X_Start:self.Crop_X_Start+self.Crop_Width, self.Crop_Y_Start:self.Crop_Y_Start+self.Crop_Height]
                blur = cv2.blur(crop,(5,5))
                # find the traveler
                lowerB=np.array([int(self.slider_B_lower_value*2.55),int(self.slider_G_lower_value*2.55),int(self.slider_R_lower_value*2.55)])
                upperB=np.array([int(self.slider_B_upper_value*2.55),int(self.slider_G_upper_value*2.55),int(self.slider_R_upper_value*2.55)])
                maskB=cv2.inRange(blur,lowerB,upperB)
                # opening and closing
                kernelOpen=np.ones((5,5))
                kernelClose=np.ones((15,15))

                maskOpenB=cv2.morphologyEx(maskB,cv2.MORPH_OPEN,kernelOpen)
                maskCloseB=cv2.morphologyEx(maskOpenB,cv2.MORPH_CLOSE,kernelClose)
                maskCloseB_rgb = cv2.cvtColor(maskCloseB, cv2.COLOR_GRAY2BGR)

                # create transparent mask
                overlay = crop.copy()
                output = crop.copy()
                cv2.addWeighted(maskCloseB_rgb, 0.4, output, 1-0.4,0, output)

                # origin
                cxo = 350
                cyo = 309

                if self.trace_markers_FLAG == 1:
                    self.start_timer = time.time()
                    # traveler
                    im2b,contsb,hb=cv2.findContours(maskCloseB.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

                    if np.shape(contsb)[0] == 1:
                        cntB = contsb[0]
                        Mb = cv2.moments(cntB)
                        cxb = int(Mb['m10']/Mb['m00'])+self.Crop_X_Start
                        cyb = int(Mb['m01']/Mb['m00'])+self.Crop_Y_Start
                        cv2.putText(output,("Angle       = {:.2f}".format(self.azimuth*180/np.pi)),(100,100),self.font,1,(255,255,255),2,cv2.LINE_AA)
                        #cv2.putText(output,("Timer  = {:.2f}".format(time.time()-self.start_timer)),(20,100),self.font,0.8,(255,255,255),2,cv2.LINE_AA)
                        cv2.putText(output,("Revolutions = {:.0f}".format(self.rotations)),(100,150),self.font,1,(255,255,255),2,cv2.LINE_AA)
                        cv2.putText(output,("Tubes RPM = {:.2f}".format(self.rpm)),(100,200),self.font,1,(255,255,255),2,cv2.LINE_AA)
                        cv2.putText(output,("Tubes RCF  = {:.2f}".format(1.118*15*(self.rpm**2)*1e-6)),(100,250),self.font,1,(255,255,255),2,cv2.LINE_AA)
                    else:
                        cxb = cxo
                        cyb = cxo
                        cv2.putText(output,'Marker has been lost',(200,250),self.font,1,(0,0,255),2,cv2.LINE_AA)


                    cv2.circle(output,(cxo,cyo),10,(0,255,0),-1)
                    cv2.circle(output,(cxb,cyb),10,(255,250,0),-1)

                    # radius
                    cv2.line(output,(cxo,cyo),(cxb,cyb),(0,255,0),3)
                    radius = int(np.sqrt((np.absolute(cxb-cxo))**2+(np.absolute(cyb-cyo))**2))

                    # circumference
                    cv2.circle(output,(cxo,cyo),10,(0,255,255),-1)
                    cv2.circle(output,(cxo,cyo),radius,(0,255,0),2)

                    # azimuth
                    cv2.arrowedLine(output,(cxo,cyo),(cxo,cyo-50),(255,255,255),2)

                    # calculate azimuth
                    #self.azimuth = np.arcsin((cxb-cxo)/radius)
                    if cxb==cxo or cyb==cyo:
                        pass
                    elif cxb<cxo and cyb<cyo:
                        self.azimuth=np.arcsin((cxo-cxb)/radius)
                    elif cxb<cxo and cyb>cyo:
                        self.azimuth=np.arcsin((cxo-cxb)/radius)+np.pi/2
                    elif cxb>cxo and cyb>cyo:
                        self.azimuth=np.arcsin((cxb-cxo)/radius)+np.pi
                    elif cxb>cxo and cyb<cyo:
                        self.azimuth=np.arcsin((cxb-cxo)/radius)+np.pi*3/2

                    # calculate RPM (values 0.85 and 9 have been calibrated experimentally)
                    if np.round(self.azimuth,2) <= 0.85 and (self.count-self.prev_count)>9:
                    # calculate RPM (values 0.75 and 8 have been calibrated experimentally)
                    #if np.round(azimuth,2) <= 0.75 and (count-prev_count)>8:
                        self.count=0
                        self.rpm = 60*self.gear_ratio/(time.time()-self.previous_time)
                        self.rcf = 1.118*self.tube_length*self.rpm**2*1e-6
                        self.previous_time = time.time()
                        self.rotations = self.rotations+1
                        self.prev_count = self.count
                        if self.rotations >= self.graph_x_size:
                            self.rotations = 0
                            self._dynamic_ax.clear()
                            self.rpm2=np.zeros(self.graph_x_size)
                            self.rcf2=np.zeros(self.graph_x_size)

                        self.rpm2[self.rotations] = self.rpm # goes to plot
                        self.rcf2[self.rotations] = self.rcf # goes to plot
                    
                    self.count = self.count+1
                #-----------------------------end of trace_markers_FLAG-----------------------------------------------------

                cv2.putText(output,"MTU MOST Centrifuge CAM",(20,30),self.font,1,(55,255,255),2,cv2.LINE_AA)  
                cv2.putText(output,("Timer  = {:.2f}".format(time.time()-self.start_timer)),(400,550),self.font,1,(255,255,255),2,cv2.LINE_AA) 
                
                # write a video file
                #out.write(output) 
                # display the output frame
                cv2.imshow("MTU MOST Centrifuge", output)  
           
                # Press Q on keyboard to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # release the video capture object and close all frames
                    cap.release()
                    cv2.destroyAllWindows()
                    break
            else:
                break
# ---------------------------end of btn_OPEN_VID_click_function-----------------------------------------------------------------



    def btn_SET_ROI_function(self):
        self.Crop_X_Start = np.int64(self.textbox_CROP_X.text())
        self.Crop_Y_Start = np.int64(self.textbox_CROP_Y.text())
        self.Crop_Width = np.int64(self.textbox_CROP_WIDTH.text())
        self.Crop_Height = np.int64(self.textbox_CROP_LENGTH.text())


    def btn_TRACE_MARKERS_function(self):
        self.trace_markers_FLAG = 1

    def btn_RESET_TIMER_function(self):
        self.spin_time = time.time()

    def slider_R_lower_change(self):
        self.slider_R_lower_value = self.slider_R_lower.value()
        print("R lower  = {:.2f}".format(self.slider_R_lower_value))

    def slider_R_upper_change(self):
        self.slider_R_upper_value = self.slider_R_upper.value()
        print("R upper  = {:.2f}".format(self.slider_R_upper_value))

    def slider_G_lower_change(self):
        self.slider_G_lower_value = self.slider_G_lower.value()
        print("G lower  = {:.2f}".format(self.slider_G_lower_value))

    def slider_G_upper_change(self):
        self.slider_G_upper_value = self.slider_G_upper.value()
        print("G upper  = {:.2f}".format(self.slider_G_upper_value))

    def slider_B_lower_change(self):
        self.slider_B_lower_value = self.slider_B_lower.value()
        print("B lower  = {:.2f}".format(self.slider_B_lower_value))

    def slider_B_upper_change(self):
        self.slider_B_upper_value = self.slider_B_upper.value()
        print("B upper  = {:.2f}".format(self.slider_B_upper_value))


    def btn_SET_GEAR_RATIO_clicked(self):
        self.gear_ratio = float(self.textbox_GEAR_RATIO.text())


    def btn_RCF_OF_RPM_function(self):
        figure_1 = plt.figure('RCF(RPM) Function')
        plt.plot(self.rpm2,self.rcf2,'o',color='#0000FF') # experimental data

        tt = np.linspace(0,10*self.graph_x_size,self.graph_x_size)
        plt.plot(tt,1.118*self.tube_length*tt**2*1e-6,color='#DC143C') # theoretical data
        plt.grid()
        plt.legend(['Experimental data','Theoretical calculation'])
        plt.xlabel('Radial Velocity, rpm')
        plt.ylabel('Relative Centrifugal Force, N')
        plt.title('Computed RCF of the test tubes')
        plt.show(figure_1)


    def _update_canvas(self):
        
        self._dynamic_ax.set_title('Sound')
        t = np.linspace(0, self.graph_x_size, self.graph_x_size)
        self._dynamic_ax.clear()

        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t,self.rpm2,color='#696969')
        self._dynamic_ax.fill_between(t,0,self.rpm2,facecolor='#696969')
        self._dynamic_ax.plot(0,0,color='#B0C4DE')
        self._dynamic_ax2.plot(t,self.rcf2,color='#B0C4DE')
        self._dynamic_ax2.fill_between(t,0,self.rcf2,facecolor='#B0C4DE')
        self._dynamic_ax.axvline(x=self.rotations,linewidth=2,c='r')
        self._dynamic_ax.set_title('Centrifuge Spin Test')
        self._dynamic_ax.set_ylabel('Radial Velocity, rpm')
        self._dynamic_ax.set_xlabel('Number of Revolutions')
        self._dynamic_ax.legend(['Tubes RPM','Tubes RCF'])
        #self._dynamic_ax2.legend(['RCF'])

        self._dynamic_ax.grid()
        #self._dynamic_ax.set_yticks(np.arange(-1.3, 1.6, step=0.2))

        self._dynamic_ax.figure.canvas.draw()

        self.lbl_TIMER_seconds.setText(str(np.round(time.time()-self.spin_time,2))+" s")
        self.lbl_BIG_RPM.setText(str(np.round(self.rpm,2))+" RPM")
        self.lbl_BIG_RCF.setText(str(np.round(self.rcf,2))+" RCF")



#------------------------ MAIN -------------------------

def main():
   app = QApplication(sys.argv)
   ex = App()
   ex.show()
   sys.exit(app.exec_())


if __name__ == '__main__':
    main()

#------------------------ END -------------------------

