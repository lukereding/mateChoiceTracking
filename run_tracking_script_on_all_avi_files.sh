#!/bin/bash

# this bash script loops through all the files in the current directory and runs the tracking script on them,
# naming log files and the trials accordingly

for file in ./*.avi
do
	# find file name w/o extension
	PATH_OF_TRIAL=${file%.avi}
	NAME_OF_TRIAL=${PATH_OF_TRIAL##*/}
	echo $NAME
	python /Users/lukereding/Desktop/mateChoiceTracking/realTimeTrackerShort.py -i $file -n $NAME_OF_TRIAL -f 10 >> "$NAME""_log.txt"
done