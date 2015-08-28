#!/usr/bin/env
import numpy as np
import cv2, csv, os, re, sys, time, argparse, datetime


'''
started 25 August 2015

typical useage:
-- run this script at the beginning of a 10 minute acclimation period (this time can be changed with the -l parameter)
-- outline the rectangle along the bounds of the tank
-- wait for the camera to detect the background
-- the program starts automatically and shuts off 20 minutes later. You can tweak this amount of time with the -t parameter
-- a video file, list of association zones occupied, a csv file containing coordinates are all saved in the directory where you ran the script from
-- association time stats are spit out at the end. the fish is tested for side bias in the 2nd and 4th quarters of the trial period

assumes there are four 'parts' to your video of each length. this only affects some of the stats the program prints at the end

important: the long side of the tank must be perpendicular to the camera view

as currently written, if given a video argument, the program will not spit out association time stats

this here is a working copy of a python script I hope to use to accomplish the following:
-- track fish in mate choice tank in real time
-- save videos from each experiment
-- have the experimenter record the bounds of the fish tank
-- have the tracker record association time in real time
-- have the program output error messages / let the experimenter know if there were problems with the tracker 
or if the fish needs to be re-tested
-- ensure constant framerate
-- track progress for detecting background??
-- incorporating all four parts of each trial

help menu:  python realTimeTracker.py --help

arguments:
--inputCamera: defaults to 0. typically 0 or 1
--videoName: used to save files associated with the trial. required
--lengthOfAcclimation: time in seconds between when you press Enter and when the program starts tracking. Should be >60. defaults to 600
--lengthOfTrial: time is seconds of the trial excluding the acclimation time

example of useage: python realTimeTracker.py -i /Users/lukereding/Desktop/Bertha_Scototaxis.mp4 -n jill

typical useage for my mate choice trials: python realTimeTracker.py -n nameOfTrialGoesHere
'''


# initialize some constants, lists, csv writer
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputCamera", help = "integer that represents which usb input the camera is. typically 0 or 1. can also be the fill path to a video file",nargs='?',default=0)
ap.add_argument("-n", "--videoName", help = "name of the video to be saved",required=True)
ap.add_argument("-l", "--lengthOfAcclimation", help = "length of time (in seconds) between when you start the program and when it starts tracking. defaults to 600",nargs='?',default=600,type=int)
ap.add_argument("-t", "--lengthOfTrial", help = "length of trial (in seconds). defaults to 1200",nargs='?',default=1200,type=int)
ap.add_argument("-b", "--bias", help = "proportion of time a fish spends on either the right or lefthand side of the tank to be declared side bias. defaults to 0.75",nargs='?',default=0.75)

args = ap.parse_args()

# print arguments to the screen
print("\n\n\tinput camera: {}".format(args.inputCamera))
print("\tname of trial: {}".format(args.videoName))
print("\tlength of trial excluding acclimation: {}".format(args.lengthOfTrial))
print("\tbias: {}".format(args.bias))
print "\tlength of acclimation: {}".format(args.lengthOfAcclimation) + "\n\n"
args = vars(ap.parse_args())

# enter a check for acclimation time. just want to ensure that acclimation time is long enough that it doesn't interfere with calculating the background image
acclimationLength = args["lengthOfAcclimation"]
if acclimationLength < 40:
	sys.exit("enter a longer acclimation time. The acclimation time needs to be long enough that a background image can be computed (~60 seconds)")
lengthOfTrial = args["lengthOfTrial"]
bias = args["bias"]
if bias > 1 or bias < 0:
	sys.exit("bias (-b) must be between 0 and 1")

# calculate the time that the program should start the main loop
start_time = time.time()
end_time = start_time + acclimationLength

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
print "python version:\n"
print sys.version 

######################
# declare some functions:####
#####################################

def checkSideBias(left,right,neutral,bias):
	
	total = left + right + neutral
	if left >= bias*total:
		return("left side bias")
	elif right >= bias*total:
		return("right side bias")
	else:
		return("looks good")

def printUsefulStuff(listOfSides,fps,biasProp):
	
	# print realized fps for the trial
	print "\n\n\n\nrealized fps: " + str(fps)
	print "\ntotal frames: " + str(len(listOfSides))
	
	# now subset the list of sides into four parts. each will be a quarter of the total length of the list
	# there is probably a better way to do this, but I don't know what it is
	leftPart1 = listOfSides[0:int(len(listOfSides)*0.25)].count("left")
	rightPart1 = listOfSides[0:int(len(listOfSides)*0.25)].count("right")
	neutralPart1 = listOfSides[0:int(len(listOfSides)*0.25)].count("neutral")
	
	leftPart2 = listOfSides[int(len(listOfSides)*0.25):int(len(listOfSides)*0.5)].count("left")
	rightPart2 = listOfSides[int(len(listOfSides)*0.25):int(len(listOfSides)*0.5)].count("right")
	neutralPart2 = listOfSides[int(len(listOfSides)*0.25):int(len(listOfSides)*0.5)].count("neutral")
	
	leftPart3 = listOfSides[int(len(listOfSides)*0.5):int(len(listOfSides)*0.75)].count("left")
	rightPart3 = listOfSides[int(len(listOfSides)*0.5):int(len(listOfSides)*0.75)].count("right")
	neutralPart3 = listOfSides[int(len(listOfSides)*0.5):int(len(listOfSides)*0.75)].count("neutral")
	
	leftPart4 = listOfSides[int(len(listOfSides)*0.75):len(listOfSides)].count("left")
	rightPart4 = listOfSides[int(len(listOfSides)*0.75):len(listOfSides)].count("right")
	neutralPart4 = listOfSides[int(len(listOfSides)*0.75):len(listOfSides)].count("neutral")
	
	# print association time stats to the screen for each part
	print "------------------------------\n\n\n\n\n\n\nassociation time statistics for each part of the trial:"
	print "\n\npart 1:\nframes 0 - " + str(int(len(listOfSides)*0.25))
	print "seconds left: " + str(leftPart1/fps)
	print "seconds right: " + str(rightPart1/fps)
	print "seconds neutral: " + str(neutralPart1/fps) + "\n"
	print checkSideBias(leftPart1,rightPart1,neutralPart1,biasProp)
	
	# print association time stats to the screen for each part
	print "\n\npart 2:\nframes " + str(int(len(listOfSides)*0.25)) + " - " + str(int(len(listOfSides)*0.5))
	print "seconds left: " + str(leftPart2/fps)
	print "seconds right: " + str(rightPart2/fps)
	print "seconds neutral: " + str(neutralPart2/fps) + "\n"
	print checkSideBias(leftPart2,rightPart2,neutralPart2,0.75)
	
	# print association time stats to the screen for each part
	print "\n\npart 3:\nframes " + str(int(len(listOfSides)*0.5)) + " - " + str(int(len(listOfSides)*0.75))
	print "seconds left: " + str(leftPart3/fps)
	print "seconds right: " + str(rightPart3/fps)
	print "seconds neutral: " + str(neutralPart3/fps) + "\n"
	print checkSideBias(leftPart3,rightPart3,neutralPart3,biasProp)
	
	# print association time stats to the screen for each part
	print "\n\npart 4:\n" + str(int(len(listOfSides)*0.75)) + " - " + str(int(len(listOfSides)))
	print "seconds left: " + str(leftPart4/fps)
	print "seconds right: " + str(rightPart4/fps)
	print "seconds neutral: " + str(neutralPart4/fps) + "\n"
	print checkSideBias(leftPart4,rightPart4,neutralPart4,biasProp)
	
	## check for side bias in the two parts where stimuli were present:
	print "\n\nchecking side bias for parts 2 and 4, where male stimuli were present:\n\n"
	print "left: " + str((leftPart2+leftPart4)/fps) + "\nright: " + str((rightPart2+rightPart4)/fps) + "\nneutral: " + str((neutralPart2+neutralPart4)/fps)
	bias = checkSideBias(leftPart2+leftPart4,rightPart4+rightPart2,neutralPart4+neutralPart2,biasProp)
	print bias
	if bias != "looks good":
		print "\tFEMALE MUST BE RE-TESTED. SET ASIDE FEMALE AND RE-TEST AT A LATER DATE"
	

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
		top_bound, left_bound, right_bound, lower_bound = iy*2, ix*2, x*2, y*2
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
	return mask

	
# returns centroid from largest contour from a binary image
def returnLargeContour(frame,totalVideoPixels):
	potential_centroids = []
	
	# find all contours in the frame
	contours = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
	print "number of contours: " + str(len(contours)) + "\n"
	
	for z in contours:
		# calculate some things
		area = cv2.contourArea(z)
		x,y,w,h = cv2.boundingRect(z)
		aspect_ratio = float(w)/h
		
		##### the main filtering statement:
		# the problem with use absolute values for the size cutoffs is that this will vary with the dimensions of the camera
		# I originally found that including blobs within the range (150, 2000) worked well for videos that were 1280x780
		# thus the fish took up ~0.016776% to ~0.21701% of the total available pixels (921,600)
		# based on that, I should be able to apply those percents to any video resolution and get good results 
		if area > (totalVideoPixels*0.00016776) and area < (totalVideoPixels*0.0021701) and aspect_ratio <= 3.5 and aspect_ratio >= 0.3:
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
	
	print "\n\n\n\n-----------------------\n\ninitializing background detection\n"
	
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
		cv2.accumulateWeighted(frame,update,0.001)
		final = cv2.convertScaleAbs(update)
		# increment the counter
		i += 1
		
		# print something every 100 frames so the user knows the gears are grinding
		if i%100 == 0:
			print "detecting background -- on frame " + str(i) + " of " + str(numFrames)
	return final

def waitHere(end):
	while(time.time() < end):
		if round(end - time.time(),1) % 5 == 0:
			print "starting in " + str(int(end - time.time())) + " seconds"  
		time.sleep(0.1)
#########################
## end function declarations ####
###################################################

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
print "\n\ncamera feed dimensions: " + str(camWidth) + " x " + str(camHeight)

# grab the first few frames to let the camera warm up
i = 1
while(i < 15):
	ret,frame = cap.read()
	i += 1
#resize
frameResized = cv2.resize(frame,(0,0),fx=0.5,fy=0.5)

# loop to have the user draw the rectangle
print "\n\n\n\n\ndraw rectangle from left to right.\npress esc when you're done drawing the rectangle"
while(True):
	cv2.namedWindow('tank')
	cv2.setMouseCallback('tank',frameResized)
	cv2.imshow('tank',frame)
	k = cv2.waitKey(1) & 0xFF
	if k == 27:
		cv2.destroyAllWindows()
		break

# need to do this step after the drawing the rectangle so that we know the bounds for masking in the call to convertToHSV
#hsv_initial = convertToHSV(frame)

# calculate background image of tank for 1500 frames
background = getBackgroundImage(cap,1500)
hsv_initial = convertToHSV(background)
cv2.imwrite(name + "_background.jpg",background)

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

# wait until the acclimation period is over, then start the loop
waitHere(end_time)

startOfTrial = time.time()
###########################
### the main loop######
###################
while(time.time() - startOfTrial < lengthOfTrial):
	
	print "frame " + str(counter) + "\n\n"
	
	# wait until the 10 minutes while the fish is acclimating is up
	while(time.time() < end_time):
		if round(end_time - time.time(),1) % 5 == 0:
			print "starting in " + str(int(end_time - time.time())) + " seconds" 
			# wait 0.1 seconds
		time.sleep(.1)
	
	# for calculating realized fps later on
	if counter == 0:
		beginningOfTrial = time.time()
	
	# for timing, maintaining constant fps
	beginningOfLoop = time.time()
	
	ret,frame = cap.read()
	cv2.putText(frame,str(datetime.datetime.now().strftime("%D %H:%M:%S.%f")), (20,20),cv2.FONT_HERSHEY_PLAIN, 1.0,(255,255,255))
	# save the frame to the video
	videoWriter.write(frame)
	
	# do image manipulations for tracking
	hsv = convertToHSV(frame)
	difference = cv2.subtract(hsv_initial,hsv)
	masked = cv2.inRange(difference,lower,upper)
	maskedInvert = cv2.bitwise_not(masked)

	# find the centroid of the largest blob
	center = returnLargeContour(maskedInvert, camWidth*camHeight)
		
	# if the fish wasn't ID'ed by the tracker, assume it's stopped moving
	if not center:
		coordinates.append(coordinates[-1]) 
	# otherwise add the coordinate to the growing list
	else:
		coordinates.append(center)
	
	print "coordinates: " + str(coordinates[-1])
	
	# find what association zone the fish is in:
	if coordinates[-1][0] < leftBound:
		zone.append("left")
	elif coordinates[-1][0] > rightBound:
		zone.append("right")
	else:
		zone.append("neutral")

	
	print "Center: " + str(center) + "\n"
	
	# draw the centroids on the image
	cv2.circle(frame,coordinates[-1],6,[0,0,255],-1)
	
	cv2.putText(frame,str(zone[-1]),(leftBound,lower_bound+50), cv2.FONT_HERSHEY_PLAIN, 3.0,(255,255,255))
	cv2.putText(frame,str("frame " + str(counter)), (leftBound,lower_bound+150),cv2.FONT_HERSHEY_PLAIN, 3.0,(255,255,255))
	
	#resize image for the laptop
	frame = cv2.resize(frame,(0,0),fx=0.5,fy=0.5)
	cv2.imshow('image',frame)
	#cv2.imshow('thresh',masked)
	#cv2.imshow('diff',difference)
	
	# each loop should take 0.2 seconds to ensure a framerate of 5 fps
	endOfLoop = time.time()
# 	try:
# 		print endOfLoop-beginningOfLoop
# 		time.sleep(0.17-(endOfLoop-beginningOfLoop))
# 	except:
# 		pass
	
	print "time of loop: " + str(round(time.time()-beginningOfLoop,4))
	
	k = cv2.waitKey(1)
	if k == 27:
		break

	# the idea here is to re-set the 'initial' image every 150 frames in case there are changes with the light or top of the water reflections
#	if counter % 150 ==0:
#		hsv_initial = hsv

	counter+=1


########################
##### end of main loop #####
###################################

# save list of association zones
output = open(name+'.txt', 'wb')
for line in zone:
	output.write("%s\n" % line)
output.close()

### after the program exits, print some useful stuff to the screen
# first calculate realized fps
print "counter: " + str(counter)
print "total time: " + str(endOfLoop-beginningOfTrial)
realizedFPS = counter / (endOfLoop-beginningOfTrial)

# calculate and print association time to the screen
printUsefulStuff(zone, realizedFPS,bias)

print "\n\nCongrats. Lots of files saved.\n\n\tYour video file is saved at " + str(pathToVideo) + "\n\tYour csv file with tracking coordinates is saved at " + os.getcwd() + "/" + name + ".csv"
print "\tYour list of tentative association zones occupied in each frame is saved at " + os.getcwd() + "/" + name + ".txt"


cv2.destroyAllWindows()