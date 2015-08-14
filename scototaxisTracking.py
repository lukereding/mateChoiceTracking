#!/usr/bin/env
import numpy as np
import cv2, csv, os, re
import argparse
import warnings

'''
15 August 2015

this function calculates that percent of time a fish spends on the white side of a black/white tank
it uses a subtraction algorithm to identify the fish

usage example: python scototaxisTracking.py -i /Users/lukereding/Desktop/video.mp4
the results will be saved as /Users/lukereding/Desktop/video.csv

things you might need to change:
-- the mask bounds -- everything outside these bounds are discarded
-- the minimum contour size
-- the contour aspect ratio

The script assumes your videos are 1280x720
if not, use 
'''

#######################
# declare some functions: ####
##########################################

# converts a frame to HSV, blurs it, masks it to only get the tank by itself
def convertToHSV(frame):
	blurred = cv2.blur(frame,(5,5))
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
 	mask = np.zeros((720, 1280, 3),np.uint8)
 	mask[90:650,60:1200] = hsv[90:650,60:1200]
	return mask

# this function takes a video as input and uses a 'running average' to estimate what the background should look like
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

	
# returns centroid from largest contour from a binary image
def returnLargeContour(frame):
	potential_centroids = []
	
	# find all contours in the frame
	contours = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
	print "number of contours: " + str(len(contours))
	
	# for each contour:
	for z in contours:
		# calculate some things
		area = cv2.contourArea(z)
		x,y,w,h = cv2.boundingRect(z)
		aspect_ratio = float(w)/h
		
		#the main filtering statement
		if area > 50 and area < 1000 and aspect_ratio <= 5 and aspect_ratio >= 0.20:
			potential_centroids.append(z)
			print "potential centroids: \n"
			print "area: " + str(area) + "; aspect ratio: " + str(aspect_ratio)
		
	
	# sort by size
	largestCon = sorted(potential_centroids, key = cv2.contourArea, reverse = True)[:1]
	
	# there aren't any contours that pass the filtering steps above, write NAs to the csv
	if len(potential_centroids) == 0:
		csv_writer.writerow(("NA","NA",counter))
		return()
	
	# if the list is not empty, return the centroid of largestCon and print the centroid to the screen
	else:
		m = cv2.moments(largestCon)		
		centroid_x = int(m['m10']/m['m00'])
		centroid_y = int(m['m01']/m['m00'])
		csv_writer.writerow((centroid_x,centroid_y,counter))
		return((centroid_x,centroid_y))

###########################
### end function declarations #######
##############################################


print "\nyou are running scototaxisTracking.py\n\n"

# initialize some constants, lists, csv writer
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputVideo", help = "path to the video")
args = vars(ap.parse_args())
lower = np.array([0,0,0])
upper = np.array([255,255,30])
counter = 0

# set up the video capture to the video that was the argument to the script
cap = cv2.VideoCapture(args["inputVideo"])

# output to csv file where the results will be written
name = re.split('[/.]', args["inputVideo"], flags=re.IGNORECASE)[-2]
name = name + ".csv"
print "name of csv file: " + name + "\n\n"
myfile = open(name,'wb')
csv_writer = csv.writer(myfile, quoting=csv.QUOTE_NONE)
csv_writer.writerow(("x","y","frame"))

# make sure your videos are the right size
# if not, issue a warning
# (in the future, use os.system() to call ffmpeg or add variable that will rescale each photo in the main loop)
_,frame=cap.read()
if frame.shape[0] != 720:
	warn("this script is meant for videos that are 1280x720. It appears this video is not. Note that this will probably cause problems, espeically when masking.")


## get the background image
# fancy way:
# get the background image and convert to HSV
# background = getBackgroundImage(cap,500)
# background = convertToHSV(background)

# simple way:
# this is really all we need since we're using cv2.subtract and not cv2.absdiff in the while loop below
_,background = cap.read()
background = convertToHSV(background)

# the main loop
while(cap.isOpened()):

	print "frame " + str(counter)
	
	if counter == 0:
		# re-start the video capture
		cap = cv2.VideoCapture(args["inputVideo"])
		counter = 1
		
	else:
		_,frame = cap.read()
		hsv = convertToHSV(frame)
		difference = cv2.subtract(background,hsv)
		masked = cv2.inRange(difference,lower,upper)
		maskedInvert = cv2.bitwise_not(masked)
		
		# find the centroid of the largest blob
		center = returnLargeContour(maskedInvert)
		print "Center: " + str(center)
		# draw the centroids on the image
		if not not center:
			cv2.circle(frame,center,6,[0,0,255],-1)
		# to save the frames:
		#filename = "/Users/lukereding/Desktop/example/" + "{0:05d}".format(counter) + ".jpg"
		#cv2.imwrite(filename,frame)
		
		cv2.imshow('image',frame)
		cv2.imshow('thresh',masked)
		cv2.imshow('diff',difference)
		
		k = cv2.waitKey(1)
		if k == 27:
			break
		
		counter+=1

cv2.destroyAllWindows()