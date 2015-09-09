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
## ./makingVideosForMateChoiceExperiments.sh nameOfVideo1.avi nameOfVideo2.avi


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
#######################

# 
# FILES=/path/to/*
# for f in $FILES
# do
#   echo "Processing $f file..."
#   # take action on each file. $f store current file name
#   cat $f
# done

####################################




# use this to concatenate
## note: the videos must be the same size 
# you can use something like ffmpeg -i flipped5min.mp4 -vf scale=1280:720 flipped5minScaled.mp4
# to scale them if they aren't
ffmpeg -i countdown5minFlipped.mp4 -vcodec libx264 v1.mp4
ffmpeg -i flipped5min.mp4 -vcodec libx264 v2.mp4
echo "file 'v1.mp4'" > listOfVideos
echo "file 'v2.mp4'" >> listOfVideos
ffmpeg -f concat -i listOfVideos -c copy -y videoConcat.avi


# for looping
for i in {1..12}; do printf "file '%s'\n" largeNigrinsisCourtingBIG.mp4 >> list.txt; done
ffmpeg -f concat -i list.txt -c copy largeMaleCourting.mp4


# for overlaying one video onto another
# see https://trac.ffmpeg.org/wiki/Create%20a%20mosaic%20out%20of%20several%20input%20videos
ffmpeg -i background5min.mp4 -i flipped5Min.mp4 -filter_complex "nullsrc=size=1920x1080 [base]; [0:v] setpts=PTS-STARTPTS, scale=1920x1080 [backgroundVideo]; [1:v] setpts=PTS-STARTPTS, scale=800x480 [upperMiddleFish]; [base][backgroundVideo] overlay=shortest=1 [tmp1]; [tmp1][upperMiddleFish] overlay=shortest=1:x=700" -c:v libx264 -y output.mkv


### making background video (where the image is the only .jpg in your directory):
ffmpeg -framerate 1/150 -i *.jpg -r 15 background.mp4


############################# 


##### black video
ffmpeg -framerate 1/300 -i black.jpg -r 25 black.mp4

##### countdown
# scale the countdown by the resolution of your monitor
# make 25 fps
# flip it
ffmpeg -i *count*.mp4 -vf -r 25 scale=1280:1024 final10MinCountdown.mp4

####### background video
# if the dimensions of background.jpg are not even numbers, this will throw an error
# make the video at 25 fps
# flip it
ffmpeg -framerate 1/300 -i *.jpg -r 25 -vf "hflip,vflip,format=yuv420p" background5min.mp4


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














