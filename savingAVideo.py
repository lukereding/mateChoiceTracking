import numpy as np
import cv2, argparse, time, datetime

"""
example useage: python savingAVideo.py -r 10 -n testing -i 0
"""


beginningTime = time.time()

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--videoName", help = "name of the video to be saved",required=True)
ap.add_argument("-i", "--inputStream", help = "input stream. typically 0 or 1. defaults to 1",default=1,type=int)
ap.add_argument("-r", "--recordingTime", help = "how many seconds do you want to the program to record for? defaults to 20 min",default=1200,type=int,required=True)
ap.add_argument("-w", "--waitingTime", help = "how many seconds do you want the program to wait for before it begins? defaults to 10 min",default=600,type=int,required=True)

args = ap.parse_args()

# print arguments to the screen
print("\n\n\tname of trial: {}".format(args.videoName))
print("\tinput: {}".format(args.inputStream))
print("\twaitingTime: {}".format(args.waitingTime))
print("\tlength of time to record: {}".format(args.recordingTime)+"\n")

args = vars(ap.parse_args())

# enter a check for acclimation time. just want to ensure that acclimation time is long enough that it doesn't interfere with calculating the background image
name = str(args["videoName"])
input = args["inputStream"]
recordingTime = args["recordingTime"]
waiting = args["waitingTime"]

cap = cv2.VideoCapture(input)

width = cap.get(3)
height = cap.get(4)

# Define the codec and create VideoWriter object
fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
out = cv2.VideoWriter(name + '.avi',fourcc, 5.0, (int(width),int(height)))

# spin your wheels until recording starts:
while(time.time() < beginningTime + waiting):
	print beginningTime + waiting - time.time()
	time.sleep(1)

print "\n\n\n\n\n\tDONE WAITING"

counter = 0
while(time.time()-beginningTime <= recordingTime):
	ret, frame = cap.read()
	counter += 1
	if ret==True:
    	# time stamp
		cv2.putText(frame,str(datetime.datetime.now().strftime("%D %H:%M:%S.%f")), (20,20),cv2.FONT_HERSHEY_PLAIN, 1.0,(255,255,255))
		# write the frame
		out.write(frame)
		cv2.imshow('frame',frame)
		
		if counter % 100 == 0:
			print "still recording"
		
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	else:
		break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()