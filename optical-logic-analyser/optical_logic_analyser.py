######## [Includes] ########################################################################
import cv2 as cv
import numpy as np
import sys

print("Using OpenCV " + cv.__version__)

class VideoCap:
	#Data members
	_fileName = ""	#File path and name
	_stream = []	#opencv VideoCapture object
	_fps = 0.0
	_frameCount = 0
	_vidWidth = 0
	_vidHeight = 0
	_currentFrame = []

	def __init__(self, fileName):
		self._fileName = fileName
		self._stream = cv.VideoCapture(self._fileName)
		if(self._stream.isOpened() == True):
			self._fps = self._stream.get(cv.CAP_PROP_FPS)
			self._frameCount = self._stream.get(cv.CAP_PROP_FRAME_COUNT)
			self._vidWidth = self._stream.get(cv.CAP_PROP_FRAME_WIDTH)
			self._vidHeight = self._stream.get(cv.CAP_PROP_FRAME_HEIGHT)
			
			print("Opened new video file")
			print(self._fileName)
			print("Size: " + str(self._vidWidth) + "x" + str(self._vidHeight))
			print("Frames: " + str(self._frameCount))
			print("Frames per second: " + str(self._fps))

	def getFrame(self):
		retVal, self._currentFrame = self._stream.read()
		return retVal

	def showFrame(self):
		if(self._currentFrame == []):
			self.getFrame()
		picArray = np.asarray(self._currentFrame)
		cv.imshow(self._fileName, picArray)


######## [MAIN] ############################################################################
fileName = "C:\\Users\\matty\\OneDrive\\Documents\\Personal\\Projects\\optical-logic-analyser\\vid2.MP4"

vidObj = VideoCap(fileName)

#vidObj.showFrame()
#vidObj.getFrame()
vidObj.showFrame()

while(True):
	#Wait for the user to exit (press 'q')
	if((cv.waitKey(0)&0xFF) == ord('q')):
		break
	