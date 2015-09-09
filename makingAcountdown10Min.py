import cv2
import numpy as np
import os


file = raw_input("path of the folder where the pics will be saved: ")


counter=0
while 1:
	# create a blank image
	blank_image = np.zeros((550,1280,3), np.uint8)
	cv2.putText(blank_image,str(600-counter)+" seconds left",(200,300),cv2.FONT_HERSHEY_PLAIN,5.0,(255,255,255),5)
	cv2.putText(blank_image,"female free swim countdown:",(200,200),cv2.FONT_HERSHEY_PLAIN,3.0,(255,255,255),5)
	filename = file + "/" + str("%05d" % counter) + ".jpg"
	cv2.imwrite(filename,blank_image)
	counter+=1
	if counter == 601:
		break
# use ffmpeg -framerate 1 -i '%05d.jpg' -vcodec libx264 -r 20 -y countdown10min.mp4
# to stich together in ffmpeg