"""
this function calculates that percent of time a fish spends on the white side of a black/white tank

example of usage: 

started 13 August 2015, luke reding
"""

import cv2, sys, csv, re
import numpy as np
import argparse

# initialize some constants, lists, csv writer
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputVideo", help = "path to the video")
args = vars(ap.parse_args())
lower = np.array([0,0,0])
upper = np.array([50,50,50])
counter = 0

# set up the video capture to the video that was the argument to the script
cap = cv2.VideoCapture(args["inputVideo"])

# output to csv file where the results will be written
name = re.split('[/.]', args["inputVideo"], flags=re.IGNORECASE)[-2]
name = name + ".csv"
print(name)
myfile = open(name,'wb')
csv_writer = csv.writer(myfile, quoting=csv.QUOTE_NONE)
csv_writer.writerow(("x","y","frame"))


# declare some functions:


# function to determine where the fish started in the video
def findStartingPoint(video,numberOfFrames):
	# the function will go numberOfFrames frames ahead in the video and do a subtraction
	# the hope is that the fish will have moved at some point during this time
	count = 0
	# I don't know a better way to jump ahead so many frames
	while count <= numberOfFrames:
		# read in the frame for each tick of the loop
		ret,frame = video.read()
		# grab a frame from the middle. Assume the screens have turned on by then
		if count == numberOfFrames/2:
			hsv_middle = convertToHSV(frame)
		if count == numberOfFrames:
			# grab the last frame in the numberOfFrames window
			hsv_end = convertToHSV(frame)
		count += 1
		if count == 1:
			print "initializing"
		print " " * (20-(count%20)) + "." * (count%20) + "." * (count%20)
		
	# now we have masked HSV photos from the beginning, middle, and end of the initialization period
	# now we have to do some funky subtraction to get rid of the signal that results from the screen being turn on
	difference2 = cv2.subtract(hsv_end,hsv_initial)
	difference1 = cv2.subtract(hsv_end,hsv_middle)
	difference3 = cv2.subtract(difference1,difference2)
	
	# now we have what we want
	thresh = cv2.inRange(difference3,np.array([0,0,0]),np.array([255,255,25]))
	# need to invert the colors or else we run into trouble on our call to cv2.findContours
	invert = cv2.bitwise_not(thresh)
	startingPoint = returnLargeContour(invert)
	return(startingPoint)
	


# returns centroid from largest contour from a binary image
def returnLargeContour(frame):
	potential_centroids = []
	
	# find all contours in the frame
	contours = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
	print "number of contours: " + str(len(contours))
	
	for z in contours:
		# calculate some things
		area = cv2.contourArea(z)
		x,y,w,h = cv2.boundingRect(z)
		aspect_ratio = float(w)/h
		print area, aspect_ratio
		#the main filtering statement
		if area > 150 and area < 1600 and aspect_ratio <= 3.5 and aspect_ratio >= 0.3:
			potential_centroids.append(z)
			print area
			print aspect_ratio

	largestCon = sorted(potential_centroids, key = cv2.contourArea, reverse = True)[:1]

	if len(potential_centroids) == 0:
		csv_writer.writerow(("NA","NA",counter))
		return()
	else:
		for j in largestCon:	
			m = cv2.moments(j)		
			centroid_x = int(m['m10']/m['m00'])
			centroid_y = int(m['m01']/m['m00'])
			csv_writer.writerow((centroid_x,centroid_y,counter))
			if len(contours)<25:
				return((centroid_x,centroid_y))
			else:
				csv_writer.writerow(("NA","NA",counter))
				return()


## end function declarations

# grab the first frame
ret,initial = cap.read()

# the main loop
while(cap.isOpened()):

	print "frame " + str(counter)
	
	if counter == 0:
		findStartingPoint(cap,100)
		counter += 1
		# re-start the video capture
		cap = cv2.VideoCapture(args["inputVideo"])
		
	else:
		# get the next frame
		ret,frame = cap.read()
		
		#blur it
		blurred = cv2.blur(frame,(7,7))
		
		# convert to greyscale
		grey = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
		
		# do the background subtraction
		difference = cv2.subtract(initial,grey)
		
		# mask; make the image binary
		masked = cv2.inRange(difference,lower,upper)
		# invert the mask
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
		
		k = cv2.waitKey(1)
		if k == 27:
			break
		
		# if the camera 'warms up' at the beginning or the lights from the screen light up at the beginning, changing the light environment of the tank,
		# uncommenting the following lines can help
		# the idea here is to re-set the 'initial' image every 100 frames in case there are changes with the light or top of the water reflections
		#if counter % 150 ==0:
		#	hsv_initial = hsv
		
		counter+=1

cv2.destroyAllWindows()