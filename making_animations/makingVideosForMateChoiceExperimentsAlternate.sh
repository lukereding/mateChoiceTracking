#!/bin/bash

# stitching videos together using ffmpeg
# for mate choice trials
# started September 2015

## note: This is 'alternate' due to what types of videos are presented, and for how long. This is an attempt to decrease the time the fish is spent in the testing arena
# the script will provide a two videos, each of which will have the following form:
## 5 minutes of background
## 5 minutes of stimulus presentation
## 1 minute of background
## 5 minutes of stimulus presentation

# to future luke: best workflow:
## clone this repo.
## cd into this directory
## add the following ingredients:
### four animations. If you're have animations called A.avi and B.avi, you need A_flipped.avi and B_flipped.avi as well where the background in flipped
### photo of whatever background you're using, of the same dimensions as the video
### countdown
## make this script executable with chmod +x makingVideosForMateChoiceExperiments.sh
## bash - x makingVideosForMateChoiceExperiments.sh A B # for videos named A.avi, B.avi, A_flipped.avi, B_flipped.avi


# some other things:
### due to my poor bash coding abilities, the animations need to be .avi files and need to be passed as arguments to the script. the file extension should be left off but they must be avi files
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

### variables:

VID1=$1
VID2=$2
ALMOST1="$1""_almost.mp4"
ALMOST2="$2""_almost.mp4"
FINAL1="$1""_final.mp4"
FINAL2="$2""_final.mp4"
LOOPED1="$1""_looped.mp4"
LOOPED2="$2""_looped.mp4"

echo "$VID1"
echo "$VID2"
echo "$ALMOST1"
echo "$ALMOST2"
echo "$FINAL1"
echo "$FINAL2"
echo "$LOOPED1"
echo "$LOOPED2"


##### black video
### 5 minutes
ffmpeg -framerate 1/300 -i black.jpg -r 25 -y black5min.mp4
### 1 min
ffmpeg -framerate 1/60 -i black.jpg -r 25 -y black1min.mp4

####### background video
### 5 minutes
# if the dimensions of background.jpg are not even numbers, this will throw an error
# make the video at 25 fps
# flip it
ffmpeg -framerate 1/300 -i [Bb]ack*.jpg -r 25 -y background5minPre.mp4
ffmpeg -i background5minPre.mp4 -r 25 -vf "hflip,vflip,format=yuv420p" -y background5min.mp4
### 1 minute
ffmpeg -framerate 1/60 -i [Bb]ack*.jpg -r 25 -y background1minPre.mp4
ffmpeg -i background1minPre.mp4 -r 25 -vf "hflip,vflip,format=yuv420p" -y background1min.mp4

# make inset black video in in background video
### 5 min
ffmpeg -i black5min.mp4 -i background5min.mp4 -filter_complex "nullsrc=size=1280x1024 [base]; [0:v] setpts=PTS-STARTPTS, scale=1280x1024 [black]; [1:v] setpts=PTS-STARTPTS, scale=1280x550 [background]; [base][black] overlay=shortest=1 [tmp1]; [tmp1][background] overlay=shortest=1" -c:v libx264 -y FinalBackground5min.mp4
### 1 min
ffmpeg -i black1min.mp4 -i background1min.mp4 -filter_complex "nullsrc=size=1280x1024 [base]; [0:v] setpts=PTS-STARTPTS, scale=1280x1024 [black]; [1:v] setpts=PTS-STARTPTS, scale=1280x550 [background]; [base][black] overlay=shortest=1 [tmp1]; [tmp1][background] overlay=shortest=1" -c:v libx264 -y FinalBackground1min.mp4



######## animations
# assumes your animations are .avi files and that there are two of them:

## process first video
echo "Processing $VID1 video..."
# get the frame rate, codec right
ffmpeg -i "$VID1"".avi" -vcodec libx264 -r 25 -pix_fmt yuv420p -y "$VID1"".mp4"
ffmpeg -i "$VID1""_flipped.avi" -vcodec libx264 -vf "hflip,format=yuv420p" -r 25 -y "$VID1""_flipped2.mp4"
# combine the unflipped and flipped animations
echo "file '"$VID1"".mp4"'" > flipped
echo "file '"$VID1""_flipped2.mp4"'" >> flipped
ffmpeg -f concat -i flipped -vcodec copy -y "$VID1""_complete.mp4"

# loop the animation
rm list.txt
for i in {1..20}; do printf "file '%s'\n" "$VID1""_complete.mp4" >> list.txt; done
ffmpeg -f concat -i list.txt -c copy -y "$LOOPED1"
# trim down to 5 min
ffmpeg -ss 00:00:00 -t 00:05:00 -i "$LOOPED1" -vf "hflip,vflip,format=yuv420p" -y "$ALMOST1"
# embed in background
ffmpeg -i black5min.mp4 -i "$ALMOST1" -filter_complex "nullsrc=size=1280x1024 [base]; [0:v] setpts=PTS-STARTPTS, scale=1280x1024 [background]; [1:v] setpts=PTS-STARTPTS, scale=1280x550 [fish]; [base][background] overlay=shortest=1 [tmp1]; [tmp1][fish] overlay=shortest=1" -c:v libx264 -y "$FINAL1"

## process second video
echo "Processing $VID1 video..."
# get the frame rate, codec right
ffmpeg -i "$VID2"".avi" -vcodec libx264 -r 25 -pix_fmt yuv420p -y "$VID2"".mp4"
ffmpeg -i "$VID2""_flipped.avi" -vcodec libx264 -vf "hflip,format=yuv420p" -r 25 -y "$VID2""_flipped2.mp4"
# combine the unflipped and flipped animations
echo "file '"$VID2"".mp4"'" > flipped
echo "file '"$VID2""_flipped2.mp4"'" >> flipped
ffmpeg -f concat -i flipped -vcodec copy -y "$VID2""_complete.mp4"

# loop the animation
rm list.txt
for i in {1..20}; do printf "file '%s'\n" "$VID2""_complete.mp4" >> list.txt; done
ffmpeg -f concat -i list.txt -c copy -y "$LOOPED2"
# trim down to 5 min
ffmpeg -ss 00:00:00 -t 00:05:00 -i "$LOOPED2" -vf "hflip,vflip,format=yuv420p" -y "$ALMOST2"
# embed in background
ffmpeg -i black5min.mp4 -i "$ALMOST2" -filter_complex "nullsrc=size=1280x1024 [base]; [0:v] setpts=PTS-STARTPTS, scale=1280x1024 [background]; [1:v] setpts=PTS-STARTPTS, scale=1280x550 [fish]; [base][background] overlay=shortest=1 [tmp1]; [tmp1][fish] overlay=shortest=1" -c:v libx264 -y "$FINAL2"


## at this point, you should have all the videos you need. 
## now we just have to concatenate everything together
# note that whenever you concatenate videos together, all videos must have the same size and fps


## video1:
echo "file 'FinalBackground5min.mp4'" > vid1
echo "file '$FINAL1'" >> vid1
echo "file 'FinalBackground1min.mp4'" >> vid1
echo "file '$FINAL2'" >> vid1
echo "file 'FinalBackground5min.mp4'" >> vid1
ffmpeg -f concat -i vid1 -y FinalVideo1.mp4

## video2:
echo "file 'FinalBackground5min.mp4'" > vid2
echo "file '$FINAL2'" >> vid2
echo "file 'FinalBackground1min.mp4'" >> vid2
echo "file '$FINAL1'" >> vid2
echo "file 'FinalBackground5min.mp4'" >> vid2
ffmpeg -f concat -i vid2 -y FinalVideo2.mp4
