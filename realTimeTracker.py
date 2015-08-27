#!/usr/bin/env
import numpy as np
import cv2, csv, os, re, sys, time
import argparse


'''
started 25 August 2015

start this script 10 seconds before you actually want it to start to allow time for inializing
it will automatically start after 10 seconds

important: the long side of the tank must be perpendicular to the camera view

this here is a working copy of a python script I hope to use to accomplish the following:
-- track fish in mate choice tank in real time
-- save videos from each experiment
-- have the experimenter record the bounds of the fish tank
-- have the tracker record association time in real time
-- have the program output error messages / let the experimenter know if there were problems with the tracker 
or if the fish needs to be re-tested

example of useage: python realTimeTracker.py -i /Users/lukereding/Desktop/Bertha_Scototaxis.mp4 -n jill > jill
'''


# initialize some constants, lists, csv writer
# construct the argument parse and parse the arguments
start_time = time.time()
end_time = start_time + 10
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputCamera", help = "integer that represents which usb input the camera is. typically 0 or 1")
ap.add_argument("-n", "--videoName", help = "name of the video to be saved")
args = vars(ap.parse_args())
lower = np.array([0,0,0])
upper = np.array([255,255,20])
counter = 0

# output to csv file where the results will be written
name = args["videoName"]
print "name of csv file: " + str(name) + ".csv"
myfile = open(name+".csv",'wb')
csv_writer = csv.writer(myfile, quoting=csv.QUOTE_NONE)
csv_writer.writerow(("x","y","frame"))

# for drawing the rectangle around the tank at the beginning of the trial
drawing = False # true if mouse is pressed
ix,iy = -1,-1

# print python version
print "python version:"
print sys.version 

######################
# declare some functions:####
#####################################

def printUsefulStuff(listOfSides):
	# do some counting
	left = listOfSides.count("left")
	right = listOfSides.count("right")
	neutral = listOfSides.count("neutral")
	total = left + right + neutral
	
	# print association time stats to the screen
	print "\n\n\nnumber frames left: " + str(left)
	print "number frames right: " + str(right)
	print "number frames neutral: " + str(neutral) + "\n"
	
	if left >= 0.75*total:
		print "\n\n\tLEFT SIDE BIAS. RE-TEST FEMALE"
	elif right >= 0.75*total:
		print "\n\n\tRIGHT SIDE BIAS. RE-TEST FEMALE"
	else:
		print "\n\n\tno evidence of right or left side bias\n"

# set up video writer to save the video
def setupVideoWriter(width, height,videoName):
	# Define the codec and create VideoWriter object
	fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
	videoName = os.getcwd() + '/' + videoName + ".avi"
	out = cv2.VideoWriter(videoName,fourcc, 5.0, (int(width),int(height)))
	return out, videoName

# mouse callback function; draws the rectangle
def drawRectangle(event,x,y,flags,param):
    global ix,iy,drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(frame,(ix,iy),(x,y),(0,0,255),5)
        # globally define the boundaries of the tank
        global top_bound, left_bound, right_bound, lower_bound
        top_bound, left_bound, right_bound, lower_bound = iy, ix, x, y
        print "Rectangle bounds: "
        print top_bound, left_bound, right_bound, lower_bound

# converts a frame to HSV, blurs it, masks it to only get the tank by itself
## TO DO: get rid of tank bounds as global variables, include as arguments to this function
def convertToHSV(frame):
	# blur image to make color uniform
	blurred = cv2.blur(frame,(7,7))
	# conver to hsv
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	# apply mask to get rid of stuff outside the tank
	mask = np.zeros((camHeight, camWidth, 3),np.uint8)
	# use rectangle bounds for masking
	mask[top_bound:lower_bound,left_bound:right_bound] = hsv[top_bound:lower_bound,left_bound:right_bound]
	return hsv

	
# returns centroid from largest contour from a binary image
def returnLargeContour(frame):
	potential_centroids = []
	
	# find all contours in the frame
	contours = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
	print "number of contours: " + str(len(contours)) + "\n"
	
	for z in contours:
		# calculate some things
		area = cv2.contourArea(z)
		x,y,w,h = cv2.boundingRect(z)
		aspect_ratio = float(w)/h
		print area, aspect_ratio
		#the main filtering statement
		if area > 150 and area < 2000 and aspect_ratio <= 3.5 and aspect_ratio >= 0.3:
			potential_centroids.append(z)
			print "area: " + str(area) + "; aspect_ratio: " + str(aspect_ratio)

	largestCon = sorted(potential_centroids, key = cv2.contourArea, reverse = True)[:1]
	print str(len(largestCon)) + " largest contours"

	if len(potential_centroids) == 0:
		csv_writer.writerow(("NA","NA",counter))
		return(None)
	else:
		for j in largestCon:	
			m = cv2.moments(j)		
			centroid_x = int(m['m10']/m['m00'])
			centroid_y = int(m['m01']/m['m00'])
			csv_writer.writerow((centroid_x,centroid_y,counter))
			return((centroid_x,centroid_y))

# might be nice to try to get an image of the background without the fish
# computes an 'average' photo of the first numFrames frames from the video
# change lines 176 and 175 below to try it out
def getBackgroundImage(vid,numFrames):
	
	print "initializing background detection\n"
	
	# set a counter
	i = 0
	_,frame = vid.read()
	# initialize an empty array the same size of the pic to update
	update = np.float32(frame)
	
	# loop through the first numFrames frames to get the background image
	while i < numFrames:
		# grab a frame
		_,frame = vid.read()
		# main function
		cv2.accumulateWeighted(frame,update,0.01)
		final = cv2.convertScaleAbs(update)
		# increment the counter
		i += 1
		
		# print something every 100 frames so the user knows the gears are grinding
		if i%100 == 0:
			print "detecting background -- on frame " + str(i) + " of " + str(numFrames)
	return final

#########################
## end function declarations ####
###################################################

# print input argument to the terminal
print "input: " + str(args["inputCamera"])

captureNumber = args["inputCamera"]
# this is a string. If it can be converted to an integer, then convert it
try:
	int(float(captureNumber))
	captureNumber = int(captureNumber)
except:
	pass

# set up the video capture to the video that was the argument to the script, get feed dimensions
cap = cv2.VideoCapture(captureNumber)
global camWidth, camHeight # for masking
camWidth, camHeight = cap.get(3), cap.get(4)
print "camera feed dimensions: " + str(camWidth) + " x " + str(camHeight)

# grab the first frame
ret,frame = cap.read()

# loop to have the user draw the rectangle
while(True):
	cv2.namedWindow('tank')
	cv2.setMouseCallback('tank',drawRectangle)
	cv2.imshow('tank',frame)
	k = cv2.waitKey(1) & 0xFF
	if k == 27:
		cv2.destroyAllWindows()
		break

# need to do this step after the drawing the rectangle so that we know the bounds for masking in the call to convertToHSV
hsv_initial = convertToHSV(frame)

# could also try:
# background = getBackgroundImage(cap,500)
# background = convertToHSV(background)

# keep a list of coordinates of the fish.
# the idea is, for the purposes of this code, if we can't ID the fish we assume it's stopped
# the csv file we save will have NAs for these frames instead
# in R, I then go back and interpolate the missing frames
# it would be nice to have a python function at the end of this script that would do that for me, actually

# initiating with the center of the tank in case tracker can't find fish initially
# also set up left of 'left' 'right' or 'neutral' zone
center1 =(right_bound-left_bound)/2
center2 = (top_bound-lower_bound)/2
coordinates = [(center1,center2)]
zone = []

# set association zone bounds
zoneSize = int((right_bound-left_bound) / 3)
leftBound = left_bound + zoneSize
rightBound = left_bound + (2*zoneSize)

# set up video writer specifying size (MUST be same size as input) and name (command line argument)
videoWriter, pathToVideo = setupVideoWriter(camWidth, camHeight,name)


###########################
### the main loop######
###################
while(cap.isOpened()):

	print "frame " + str(counter) + "\n\n"
	
	while(time.time() < end_time):
		print "starting in " + str(round(end_time - time.time(),1)) + "seconds" 
		# wait 0.1 seconds
		time.sleep(0.1)
	
	# for timing
	beginningOfLoop = time.time()
	
	ret,frame = cap.read()
	
	# save the frame to the video
	videoWriter.write(frame)
	
	# do image manipulations for tracking
	hsv = convertToHSV(frame)
	difference = cv2.subtract(hsv_initial,hsv)
	masked = cv2.inRange(difference,lower,upper)
	maskedInvert = cv2.bitwise_not(masked)

	# find the centroid of the largest blob
	center = returnLargeContour(maskedInvert)
		
	# if the fish wasn't ID'ed by the tracker, assume it's stopped moving
	if not center:
		coordinates.append(coordinates[-1]) 
	# otherwise add the coordinate to the growing list
	else:
		coordinates.append(center)
	
	print "coordinates: " + str(coordinates[-1])
	
	# find what association zone the fish is in:
	if center == None:
		pass
	elif coordinates[-1][0] < leftBound:
		zone.append("left")
	elif coordinates[-1][0] > rightBound:
		zone.append("right")
	else:
		zone.append("neutral")

	
	print "Center: " + str(center) + "\n"
	# draw the centroids on the image
	cv2.circle(frame,coordinates[-1],6,[0,0,255],-1)
	
	if center != None:
		cv2.putText(frame,str(zone[-1]),(leftBound,lower_bound), cv2.FONT_HERSHEY_PLAIN, 3.0,(0,0,0))

	cv2.imshow('image',frame)
	cv2.imshow('thresh',masked)
	cv2.imshow('diff',difference)
	
	# print how long this loop took
	endOfLoop = time.time()
	print "time of loop: " + str(round(endOfLoop-beginningOfLoop,4))
	
	k = cv2.waitKey(1)
	if k == 27:
		break

	# the idea here is to re-set the 'initial' image every 150 frames in case there are changes with the light or top of the water reflections
	if counter % 150 ==0:
		hsv_initial = hsv

	counter+=1
###############
##### end of main loop ###
###################################

# save list of association zones
output = open(name+'.txt', 'wb')
for line in zone:
	output.write("%s\n" % line)
output.close()

### after the program exits, print some useful stuff to the screen

printUsefulStuff(zone)

print "\n\nCongrats. Lots of files saved.\n\tYour video file is saved at " + str(pathToVideo) + "\n\tYour csv file with tracking coordinates is saved at " + os.getcwd() + "/" + name + ".csv"

cv2.destroyAllWindows()
