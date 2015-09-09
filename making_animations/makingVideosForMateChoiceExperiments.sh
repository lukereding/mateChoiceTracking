#!/bin/bash

# stitching videos together using ffmpeg
# for mate choice trials
# started March 2015

# to future luke: best workflow
## clone this repo.
## navigate to this folder
## add the following ingredients:
### the two videos of what you want to show the fish
### photo of whatever background you're using, of the same dimensions as the video
## make this script executable with chmod makingVideosForMateChoiceExperiments.sh

# example of usage
## ./makingVideosForMateChoiceExperiments.sh nameOfVideo1 nameOfVideo2


# some other things:
### due to my poor bash coding abilities, the animations need to be .avi files and need to be passed as arguments to the script. the file extension should be left off
### the countdown video should have count in it and be a .mp4 file

##### Blender outputting

# The view area of the tank is 30 wide x 11 cm tall 
# This gives us an aspect ratio of 2.7. Woah!
# The resolution of the screens I'm using now, March 2015, is 1280 x 1024
# I want to output the video such that the width is equal to 1280 pixels
# The number of x pixels need to be ~550 pixels
# For some reason, Blender needs these revered, so in the Render panel change x to 1280 and y to 550 under resolution
# I've used 100 as the final bar under resolution
# I exported as a AVI RAW
# 
# I also save a photo of the background without the fish to use for the background
############################# 


##### black video
ffmpeg -framerate 1/300 -i black.jpg -framerate 25 black.mp4

##### countdown
# scale the countdown by the resolution of your monitor
# make 25 fps
# flip it
ffmpeg -i Final10Countdown.mp4 -vf -framerate 25 scale=1280:1024 final10MinCountdown.mp4

####### background video
# if the dimensions of background.jpg are not even numbers, this will throw an error
# make the video at 25 fps
# flip it
ffmpeg -framerate 1/300 -i *.jpg -framerate 25 -vf "hflip,vflip,format=yuv420p" background5min.mp4


# make inset black video in in background video
ffmpeg -i black.mp4 -i  background5min.mp4 -filter_complex "nullsrc=size=1280x1024 [base]; [0:v] setpts=PTS-STARTPTS, scale=1280x1024 [black]; [1:v] setpts=PTS-STARTPTS, scale=1280x550 [background]; [base][black] overlay=shortest=1 [tmp1]; [tmp1][background] overlay=shortest=1" -c:v libx264 -y FinalBackground5min.mp4


######## animations
# assumes your animations are .avi files and that there are two of them:

VID1=$1
VID2=$2

## process first video
echo "Processing $VID1 video..."
# get the frame rate, codec right
ffmpeg -i $VID1.avi -vcodec libx264 -y -r 25 -y $VID1.mp4
# loop the animation
for i in {1..20}; do printf "file '%s'\n" $VID1.mp4 >> list.txt; done
ffmpeg -f concat -i list.txt -c copy -y $VID1_looped.mp4
# trim down to 5 min
ffmpeg -ss 00:00:00 -t 00:05:00 -i $VID1_looped.mp4 -vf "hflip,vflip,format=yuv420p" $VID1_almost_final.mp4
# embed in background
ffmpeg -i background5min.mp4 -i $VID1_almost_final.mp4 -filter_complex "nullsrc=size=1280x1024 [base]; [0:v] setpts=PTS-STARTPTS, scale=1280x1024 [background]; [1:v] setpts=PTS-STARTPTS, scale=1280x550 [fish]; [base][background] overlay=shortest=1 [tmp1]; [tmp1][fish] overlay=shortest=1" -c:v libx264 -y $VID1_final.mp4

## process second video
echo "Processing $VID2 video..."
# get the frame rate, codec right
ffmpeg -i $VID2.avi -vcodec libx264 -y -r 25 -y $VID2.mp4
# loop the animation
for i in {1..20}; do printf "file '%s'\n" $VID2.mp4 >> list.txt; done
ffmpeg -f concat -i list.txt -c copy -y $VID2_looped.mp4
# trim down to 5 min
ffmpeg -ss 00:00:00 -t 00:05:00 -i $VID2_looped.mp4 -vf "hflip,vflip,format=yuv420p" $VID2_almost_final.mp4
# embed in background
ffmpeg -i background5min.mp4 -i $VID2_almost_final.mp4 -filter_complex "nullsrc=size=1280x1024 [base]; [0:v] setpts=PTS-STARTPTS, scale=1280x1024 [background]; [1:v] setpts=PTS-STARTPTS, scale=1280x550 [fish]; [base][background] overlay=shortest=1 [tmp1]; [tmp1][fish] overlay=shortest=1" -c:v libx264 -y $VID2_final.mp4


## at this point, you should have all the videos you need. 
## now we just have to concatenate everything together
# note that whenever you concatenate videos together, all videos must have the same size and fps


## video1:
echo "file 'final10MinCountdown.mp4'" > vid1
echo "file 'background5min.mp4'" >> vid1
echo "file '$VID1_final.mp4'" >> vid1
echo "file 'background5min.mp4'" >> vid1
echo "file '$VID2_final.mp4'" >> vid1
ffmpeg -f concat -i vid1 -y FinalVideo1.mp4

## video2:
echo "file 'final10MinCountdown.mp4'" > vid1
echo "file 'background5min.mp4'" >> vid1
echo "file '$VID2_final.mp4'" >> vid1
echo "file 'background5min.mp4'" >> vid1
echo "file '$VID1_final.mp4'" >> vid1
ffmpeg -f concat -i vid1 -y FinalVideo2.mp4














