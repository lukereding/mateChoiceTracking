#!/bin/sh

# this bash script loops through all the files in the current directory and runs the tracking script on them,
# naming log files and the trials accordingly

# set up the csv file to be written:
# make column names
echo filename,female,trial,neutral_time,time_left_part2,time_right_part2,time_neutral_part2,time_left_part3,time_right_part3,time_neutral_part3 > out.csv
	

for file in ./*_log.txt
do

	# find file name w/o extension
	PATH_OF_TRIAL=${file%.txt}
	NAME_OF_TRIAL=${PATH_OF_TRIAL##*/}
	NAME_OF_TRIAL=${NAME_OF_TRIAL%_*}
	FEMALE=${NAME_OF_TRIAL%%_*}
	TRIAL=${NAME_OF_TRIAL#*_}
	
	# find time in neutral zone, parts 2 and 3
	TIME_NEUTRAL=$(cat $file|grep 'time in neutral zone'|grep -o ':.*'|grep -o ' [0-9]*')
	
	# get times by part of time
	TIME_LEFT_PART2=$(grep 'part 2' $file -A 5| grep 'seconds left' | grep -o '[0-9].*')
	TIME_RIGHT_PART2=$(grep 'part 2' $file -A 5| grep 'seconds right' | grep -o '[0-9].*')
	TIME_NEUTRAL_PART2=$(grep 'part 2' $file -A 5| grep 'seconds neutral' | grep -o '[0-9].*')
	
	TIME_LEFT_PART3=$(grep 'part 3' $file -A 5| grep 'seconds left' | grep -o '[0-9].*')
	TIME_RIGHT_PART3=$(grep 'part 3' $file -A 5| grep 'seconds right' | grep -o '[0-9].*')
	TIME_NEUTRAL_PART3=$(grep 'part 3' $file -A 5| grep 'seconds neutral' | grep -o '[0-9].*')
	
	# 'write the csv line'
	echo $NAME_OF_TRIAL,$FEMALE,$TRIAL,$TIME_NEUTRAL,$TIME_LEFT_PART2,$TIME_RIGHT_PART2,$TIME_NEUTRAL_PART2,$TIME_LEFT_PART3,$TIME_RIGHT_PART3,$TIME_NEUTRAL_PART3 >> out.csv
	
done
