######## [Includes] ########################################################################
import cv2 as cv
import numpy as np
import sys
import math
from enum import Enum

print("Using OpenCV " + cv.__version__)

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

class SamplePoint:
	#Data members
	_name = "Unnamed"
	_x = 0
	_y = 0
	_rad = 0
	_pixelArray = []
	_avgR = 0
	_avgG = 0
	_avgB = 0
	_meterMode = ""
	_thresUpper = 0
	_thresLower = 0
	_logicLevel = 0
	_openCvDrawColour = (0, 0, 255)
	_openCvHiLightColour = (0, 255, 0)
	_highlighted = False

	def __init__(self, x, y):
		print("New sample point created")
		self.setPos(x, y)

	def setRad(self, rad):
		self._rad = int(rad)
		#print("Sample point " + self._name + " Set to radius " + str(self._rad))	

	def setPos(self, x, y):
		self._x = x
		self._y = y
		print("Sample point " + self._name + " Set to position " + str(x) + ", " + str(y))

	def getPos(self):
		return (self._x, self._y)

	def getRad(self):
		return self._rad

	def __del__(self):
		print("Sample point " + self._name + " deleted")

	def highlight(self):
		self._highlighted = True

	def unhighlight(self):
		self._highlighted = False

	def setName(self, name):
		print("Name of sampling point changed from " + self._name + " to " + name)
		self._name = name

	def getName(self):
		return self._name

	def getColour(self):
		if(self._highlighted == True):
			return self._openCvHiLightColour
		else:
			return self._openCvDrawColour

class VideoCap:
	#Data members
	#OpenCV capture object
	_stream = []	#opencv VideoCapture object
	
	#File properties
	_fileName = ""	#File path and name
	_fps = 0.0
	_frameCount = 0
	_videoLen = 0
	_vidWidth = 0
	_vidHeight = 0

	#Image array
	_currentFrame = []
	_currentFrameNum = 0
	
	#Sample point list
	_samplePoints = []
	_highlightedObject = []

	#State machine vars
	_mode = ""
	_addState = "new point centre"


	#Class constructor. Provide a file name to the video file.
	def __init__(self, fileName):
		self._fileName = fileName
		self._stream = cv.VideoCapture(self._fileName)
		if(self._stream.isOpened() == True):
			#Load information about the video file into the object for easy access.
			self._fps = self._stream.get(cv.CAP_PROP_FPS)
			self._frameCount = self._stream.get(cv.CAP_PROP_FRAME_COUNT)
			self._videoLen = self._frameCount/self._fps
			self._vidWidth = self._stream.get(cv.CAP_PROP_FRAME_WIDTH)
			self._vidHeight = self._stream.get(cv.CAP_PROP_FRAME_HEIGHT)
			
			#Print video file information to the console
			print("Opened new video file")
			print(self._fileName)
			print("Size: " + str(self._vidWidth) + "x" + str(self._vidHeight))
			print("Frames: " + str(self._frameCount))
			print("Frames per second: " + str(self._fps))
			print("Video length (sec): " + str(self._videoLen))

			#Show the first frame of the video in a window and set up the mouse callback funtion
			#for this object.
			retVal, self._currentFrame = self._stream.read()
			self._currentFrameNum = 0
			self.showFrame(self._mode)
			cv.setMouseCallback(self._fileName, self.opencvMouseEvent)

		else:
			self._stream.release()
	
	#Retrive the next frame from the video file and load it into an array
	def getNextFrame(self):
		self.getFrame(self._currentFrameNum + 1)

	#Retrive the previous frame from the video file and load it into an array
	def getPrevFrame(self):
		self.getFrame(self._currentFrameNum - 1)

	#Retrieve a specific frame from within the video
	def getFrame(self, frameNum):
		if(frameNum < 0):
			frameNum = 0
		if(frameNum > self._frameCount - 1):
			frameNum = self._frameCount - 1
		self._stream.set(cv.CAP_PROP_POS_FRAMES, frameNum)
		retVal, self._currentFrame = self._stream.read()
		self._currentFrameNum = frameNum
		print(self._currentFrameNum)

	#Display the currently loaded frame in a window. If there is no loaded frame, then load the
	#next one.
	def showFrame(self, mode):
		self._mode = mode
		outputIm = self._currentFrame.copy()
		self.drawOverlay(outputIm)
		cv.imshow(self._fileName, outputIm)

	#Draw the overlay graphics and text
	def drawOverlay(self, im):
		fontScale = 0.5
		textHeight = int(35*fontScale)

		#Default text color for the options
		addColour = (255, 0, 0)
		editColour = (255, 0, 0)
		delColour = (255, 0, 0)
		quitColour = (255, 0, 0)

		#Highlight the mode that we are in
		if(self._mode == "add"):
			addColour = (0, 255, 0)
		if(self._mode == "edit"):
			editColour = (0, 255, 0)
		if(self._mode == "delete"):
			delColour = (0, 255, 0)
		
		#Print menu text into the window
		cv.putText(im, "Add (a)", (0, 1*textHeight), cv.FONT_HERSHEY_SIMPLEX, fontScale, addColour, 1)
		cv.putText(im, "Edit (e)", (0, 2*textHeight), cv.FONT_HERSHEY_SIMPLEX, fontScale, editColour, 1)
		cv.putText(im, "Del (d)", (0, 3*textHeight), cv.FONT_HERSHEY_SIMPLEX, fontScale, delColour, 1)
		cv.putText(im, "Quit (q)", (0, 4*textHeight), cv.FONT_HERSHEY_SIMPLEX, fontScale, quitColour, 1)

		#Draw sample points
		for sp in self._samplePoints:
			cv.circle(im, sp.getPos(), sp.getRad(), sp.getColour(), 1)

	#Releases the opencv video capture object
	def release(self):
		self._stream.release()

	#Mouse event callback
	def opencvMouseEvent(self, event, x, y, flags, params):
		#Highlight object on mouse over
		if(event == cv.EVENT_MOUSEMOVE):
			#Using the current position of the mouse, determine which object (currently just
			#sampling points) should be highlighted
			selectedObjects = []
			#See which sampling points the mouse is over
			for sp in self._samplePoints:
				sp.unhighlight()
				x1, y1 = sp.getPos()
				rad = int(sp.getRad())
				if(x > (x1 - rad) and x < (x1 + rad) and y > (y1 - rad) and y < (y1 + rad)):
					selectedObjects.append(sp)

			#If there is more than one sampling point then the one with the smallest area is the
			#one that should be selected
			#If more than one is selected
			if(len(selectedObjects) > 1):
				smallestArea = 0xFFFFFFFFFFFFFFFF
				for so in selectedObjects:
					rad = so.getRad()
					area = 2*math.pi*rad
					if(area < smallestArea):
					   smallestArea = area
					   self._highlightedObject = so
			#If only one is selected
			elif(len(selectedObjects) == 1):
				self._highlightedObject = selectedObjects[0]
			#If none are selected
			else:
				self._highlightedObject = []
			#Highlight the selected object
			if(self._highlightedObject != []):
				self._highlightedObject.highlight()

		#If we are currently in add mode and there is a mouse event on the window
		if(self._mode == "add"):
			#If we are just about to add a new point
			if(self._addState == "new point centre"):
				if(event == cv.EVENT_LBUTTONUP):
					#Create new sample point and add it to the list:
					sp = SamplePoint(x, y)
					self._samplePoints.append(sp)
					#Shift to the next add sub state (set radius of point)
					self._addState = "point radius"
				return
			
			if(self._addState == "point radius"):
				#On a left click, move to the next sub state
				if(event == cv.EVENT_LBUTTONUP):
					#In the console window enter a name for the point (No mouse events).
					inputName = input("Enter name for this point (Press enter for Point" + str(self._samplePoints.index(self._samplePoints[-1])) + "):")
					if(inputName == ""):
						inputName = "Point" + str(self._samplePoints.index(self._samplePoints[-1]))
					self._samplePoints[-1].setName(inputName)
					self._addState = "new point centre"
				#On a right click, go back to placing the sample point
				if(event == cv.EVENT_RBUTTONUP):
					self._samplePoints.pop()
					self._addState = "new point centre"
				#On a mouse move, alter the radius of the sample point
				if(event == cv.EVENT_MOUSEMOVE):
					x2 = self._samplePoints[-1]._x
					y2 = self._samplePoints[-1]._y
					rad = math.sqrt((x2-x)**2 + (y2-y)**2)
					self._samplePoints[-1].setRad(rad)
				return

				self._addState == "new point centre"

		#If we are in edit mode.
		#if(self._mode == "edit"):

		#If we are and delete mode and left mouse button is pressed, delete the highlighted object.
		if(self._mode == "delete"):
			if(event == cv.EVENT_LBUTTONUP):
				if(self._highlightedObject != []):
					self._samplePoints.remove(self._highlightedObject)



######## [MAIN] ############################################################################
mainState = ""

fileName = "C:\\Users\\matty\\OneDrive\\Documents\\Personal\\Projects\\optical-logic-analyser\\vid2.MP4"

#Open video file to operate on.
vidObj = VideoCap(fileName)

while(True):
	#Look for a keypress
	keyPress = cv.waitKeyEx(10)

	#If the user presses 'a' then go into add mode
	if(keyPress == ord('a')):
		if(mainState != "add"):
			mainState = "add"
		else:
			mainState = ""
	#If the user presses 'e' then go into edit mode
	if(keyPress == ord('e')):
		if(mainState != "edit"):
			mainState = "edit"
		else:
			mainState = ""
	#If the user presses 'd' then go into del mode
	if(keyPress == ord('d')):
		if(mainState != "delete"):
			mainState = "delete"
		else:
			mainState = ""
	#If the user presses 'q', then exit
	if(keyPress == ord('q')):
		break

	#Left key
	if(keyPress == 2424832):
		vidObj.getPrevFrame()

	#Right key
	if(keyPress == 2555904):
		vidObj.getNextFrame()

	#if(keyPress != -1):
	#	print(str(keyPress))

	vidObj.showFrame(mainState)

vidObj.release()
cv.destroyAllWindows()
