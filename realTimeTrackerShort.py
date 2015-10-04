import numpy as np
import cv2, csv, os, re, sys, time, argparse, datetime


'''
started 25 August 2015
31 August 2015:
modifying script so that it queries frames from a video taken with ffmpeg
typical useage:
-- run this script at the beginning of a 10 minute acclimation period (this time can be changed with the -l parameter)
-- outline the rectangle along the bounds of the tank
-- wait for the camera to detect the background
-- the program starts automatically and shuts off 20 minutes later. You can tweak this amount of time with the -t parameter
-- a video file, list of association zones occupied, a csv file containing coordinates are all saved in the directory where you ran the script from
-- association time stats are spit out at the end. the fish is tested for side bias in the 2nd and 4th quarters of the trial period
assumes there are four 'parts' to your video of each length. this only affects some of the stats the program prints at the end
important: the long side of the tank must be perpendicular to the camera view
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
--pathToVideo: full or relative path to video file
--videoName: used to save files associated with the trial. required
example of useage: python realTimeTracker.py -i /Users/lukereding/Desktop/Bertha_Scototaxis.mp4 -n jill
typical useage for my mate choice trials: python realTimeTracker.py -n nameOfTrialGoesHere
'''


# initialize some constants, lists, csv writer
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--pathToVideo", help = "integer that represents either the relative or full path to the video you want to analyze",nargs='?',default=0)
ap.add_argument("-n", "--videoName", help = "name of the video to be saved",required=True)
ap.add_argument("-f", "--fps", help = "frames per second of the video",required=True)
ap.add_argument("-b", "--bias", help = "proportion of time a fish spends on either the right or lefthand side of the tank to be declared side bias. defaults to 0.75",nargs='?',default=0.75)

args = ap.parse_args()

# print arguments to the screen
print("\n\n\tinput path: {}".format(args.pathToVideo))
print("\tname of trial: {}".format(args.videoName))
print("\tfps of video: {}".format(args.fps))
print("\tbias: {}".format(args.bias))

args = vars(ap.parse_args())

fps = args["fps"]

bias = args["bias"]
if bias > 1 or bias < 0:
	sys.exit("bias (-b) must be between 0 and 1")

# calculate the time that the program should start the main loop
start_time = time.time()

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
	fps = int(fps)
	# print realized fps for the trial
	print "\ntotal frames: " + str(len(listOfSides))
	
	# now subset the list of sides into four parts. each will be a quarter of the total length of the list
	# there is probably a better way to do this, but I don't know what it is
	leftPart1 = listOfSides[0:int(len(listOfSides)*0.2381)].count("left")
	rightPart1 = listOfSides[0:int(len(listOfSides)*0.2381)].count("right")
	neutralPart1 = listOfSides[0:int(len(listOfSides)*0.2381)].count("neutral")
	
	# stimuli here
	leftPart2 = listOfSides[int(len(listOfSides)*0.2381):int(len(listOfSides)*0.4762)].count("left")
	rightPart2 = listOfSides[int(len(listOfSides)*0.2381):int(len(listOfSides)*0.4762)].count("right")
	neutralPart2 = listOfSides[int(len(listOfSides)*0.2381):int(len(listOfSides)*0.4762)].count("neutral")
	
	# stimuli here
	leftPart3 = listOfSides[int(len(listOfSides)*0.5238):int(len(listOfSides)*0.7619)].count("left")
	rightPart3 = listOfSides[int(len(listOfSides)*0.5238):int(len(listOfSides)*0.7619)].count("right")
	neutralPart3 = listOfSides[int(len(listOfSides)*0.5238):int(len(listOfSides)*0.7619)].count("neutral")
	
	leftPart4 = listOfSides[int(len(listOfSides)*0.7619):len(listOfSides)].count("left")
	rightPart4 = listOfSides[int(len(listOfSides)*0.7619):len(listOfSides)].count("right")
	neutralPart4 = listOfSides[int(len(listOfSides)*0.7619):len(listOfSides)].count("neutral")
	
	# print association time stats to the screen for each part
	print "------------------------------\n\n\n\n\n\n\nassociation time statistics for each part of the trial:"
	print "\n\npart 1:\nframes 0 - " + str(int(len(listOfSides)*0.2381))
	print "seconds left: " + str(leftPart1/fps)
	print "seconds right: " + str(rightPart1/fps)
	print "seconds neutral: " + str(neutralPart1/fps) + "\n"
	print checkSideBias(leftPart1,rightPart1,neutralPart1,biasProp)
	
	# print association time stats to the screen for each part
	print "\n\npart 2:\nframes " + str(int(len(listOfSides)*0.2381)) + " - " + str(int(len(listOfSides)*0.4762))
	print "seconds left: " + str(leftPart2/fps)
	print "seconds right: " + str(rightPart2/fps)
	print "seconds neutral: " + str(neutralPart2/fps) + "\n"
	print checkSideBias(leftPart2,rightPart2,neutralPart2,biasProp)
	
	# print association time stats to the screen for each part
	print "\n\npart 3:\nframes " + str(int(len(listOfSides)*0.5238)) + " - " + str(int(len(listOfSides)*0.7619))
	print "seconds left: " + str(leftPart3/fps)
	print "seconds right: " + str(rightPart3/fps)
	print "seconds neutral: " + str(neutralPart3/fps) + "\n"
	print checkSideBias(leftPart3,rightPart3,neutralPart3,biasProp)
	
	# print association time stats to the screen for each part
	print "\n\npart 4:\n" + str(int(len(listOfSides)*0.7619)) + " - " + str(int(len(listOfSides)))
	print "seconds left: " + str(leftPart4/fps)
	print "seconds right: " + str(rightPart4/fps)
	print "seconds neutral: " + str(neutralPart4/fps) + "\n"
	print checkSideBias(leftPart4,rightPart4,neutralPart4,biasProp)
	
	## check for side bias in the two parts where stimuli were present:
	print "\n\nchecking side bias for parts 2 and 3, where male stimuli were present:\n\n"
	print "left: " + str((leftPart2+leftPart3)/fps) + " seconds\nright: " + str((rightPart2+rightPart3)/fps) + "seconds\nneutral: " + str((neutralPart2+neutralPart3)/fps) + " seconds"
	bias = checkSideBias(leftPart2+leftPart3,rightPart3+rightPart2,neutralPart3+neutralPart2,biasProp)
	print bias
	
	# check for time spend in the neutral zone
	print "\nchecking for to see whether the fish spend > 50% of the trial in the neutral part of the tank:\n"
	time_neutral = int((neutralPart2+neutralPart3)/fps)
	print "time in neutral zone during parts 2 and 3: " + str(time_neutral)
	if time_neutral > 300:
		print "make a note that the female spent " + str(time_neutral/600) + "% of the trial in the neutral zone"
	
	if bias != "looks good":
		print "\tFEMALE MUST BE RE-TESTED. SET ASIDE FEMALE AND RE-TEST AT A LATER DATE"
	

# set up video writer to save the video
def setupVideoWriter(width, height,videoName):
	# Define the codec and create VideoWriter object
	fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
	videoName = os.getcwd() + '/' + videoName + ".avi"
	out = cv2.VideoWriter(videoName,fourcc, 5.0, (int(width),int(height)))
	return out, videoName


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
	mask[lower_bound:top_bound,left_bound:right_bound] = hsv[lower_bound:top_bound,left_bound:right_bound]
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

def find_tank_bounds(image,name_of_trial):
	
	# blur the image a lot
	blur = cv2.blur(image, (11,11))
	# convert to hsv
	hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
	# get only the whitish parts
	mask = cv2.inRange(hsv,np.array([0,0,144]),np.array([102,25,255]))
	
	# find all contours in the frame
	contours = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
	# find largest contour
	largestCon = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
	for j in largestCon:	
		m = cv2.moments(j)		
		centroid_x = int(m['m10']/m['m00'])
		centroid_y = int(m['m01']/m['m00'])
		x,y,w,h = cv2.boundingRect(j)
		print "x,y,w,h:"
		print x,y,w,h
		# declare the tank bounds globally
		global top_bound, left_bound, right_bound, lower_bound
		top_bound, left_bound, right_bound, lower_bound = int(y) + int(h) + 50, int(x) - 50, int(x) + 50 + int(w), int(y) - 50
		print "rectange bounds: "
		print top_bound, left_bound, right_bound, lower_bound
		
		# save a photo of the tank bounds for reference:
		# first make a copy of the image
		image_copy = image.copy()
		cv2.rectangle(image_copy,(left_bound, top_bound),(right_bound,lower_bound),(0,255,0),10)
		#cv2.rectangle(image_copy,(int(x*0.8),int(y*0.8)),(int(x*0.8)+int(w*1.2),int(y*0.8)+int(h*1.2)),(0,255,0),10)
		cv2.imwrite(str(name_of_trial) + "_tank_bounds.jpg", image_copy)

	


#########################
## end function declarations ####
###################################################

path = args["pathToVideo"]

# set up the video capture to the video that was the argument to the script, get feed dimensions
cap = cv2.VideoCapture(path)
global camWidth, camHeight # for masking
camWidth, camHeight = cap.get(3), cap.get(4)
print "\n\nvideo dimensions: " + str(camWidth) + " x " + str(camHeight)

# grab the 20th frame for drawing the rectangle
i = 0
while i <20:
	ret,frame = cap.read()
	i += 1
print "grabbed first frame? " + str(ret)

# need to do this step after the drawing the rectangle so that we know the bounds for masking in the call to convertToHSV
#hsv_initial = convertToHSV(frame)

# calculate background image of tank for x frames
background = getBackgroundImage(cap,5000)

# find the bounds of the tank:
find_tank_bounds(background,name)

# convert background to HSV and save a copy of the background image for reference
hsv_initial = convertToHSV(background)
cv2.imwrite(name + "_background.jpg",background)

# keep a list of coordinates of the fish.
# the idea is, for the purposes of this code, if we can't ID the fish we assume it's stopped
# the csv file we save will have NAs for these frames instead
# in R, I then go back and interpolate the missing frames
# it would be nice to have a python function at the end of this script that would do that for me, actually

# initiating with the center of the tank in case tracker can't find fish initially
# also set up left of 'left' 'right' or 'neutral' zone
center1 =((right_bound-left_bound)/2)+left_bound
center2 = ((lower_bound-top_bound)/2)+top_bound
coordinates = [(center1,center2)]
zone = []

# set association zone bounds
zoneSize = int((right_bound-left_bound) / 3)
leftBound = left_bound + zoneSize
rightBound = left_bound + (2*zoneSize)

# set up video writer specifying size (MUST be same size as input) and name (command line argument)
#videoWriter, pathToVideo = setupVideoWriter(camWidth, camHeight,name)


startOfTrial = time.time()
cap = cv2.VideoCapture(path)
###########################
### the main loop######
###################
while(cap.isOpened()):
	
	print "frame " + str(counter) + "\n\n"
	
	# for timing, maintaining constant fps
	beginningOfLoop = time.time()
	
	ret,frame = cap.read()
	
	if ret == False:
		print "didn't read frame from video file"
		break
	
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
	cv2.circle(frame,coordinates[-1],4,[0,0,255],-1)
	
	cv2.putText(frame,str(name),(int(camWidth/2),50), cv2.FONT_HERSHEY_PLAIN, 3.0,(255,255,255))
	cv2.putText(frame,str(zone[-1]),(leftBound,top_bound+50), cv2.FONT_HERSHEY_PLAIN, 3.0,(255,255,255))
	cv2.putText(frame,str("frame " + str(counter)), (leftBound,top_bound+100),cv2.FONT_HERSHEY_PLAIN, 3.0,(255,255,255))
	
	#resize image for the laptop
	frame = cv2.resize(frame,(0,0),fx=0.5,fy=0.5)
	cv2.imshow('image',frame)
	#masked = cv2.resize(masked,(0,0),fx=0.5,fy=0.5)
	#cv2.imshow('thresh',masked)
	#difference = cv2.resize(difference,(0,0),fx=0.5,fy=0.5)
	#cv2.imshow('diff',difference)
	
	endOfLoop = time.time()
	
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
print "\nthis program took " + str(time.time() - start_time) + " seconds to run."

# calculate and print association time to the screen
printUsefulStuff(zone,fps,bias)

print "\n\nCongrats. Lots of files saved.\n\n\tYour video file is saved at " + str(path) + "\n\tYour csv file with tracking coordinates is saved at " + os.getcwd() + "/" + name + ".csv"
print "\tYour list of tentative association zones occupied in each frame is saved at " + os.getcwd() + "/" + name + ".txt"


cv2.destroyAllWindows()
