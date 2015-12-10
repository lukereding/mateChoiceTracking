#!/usr/bin/env bash

echo $0
# read in arguments
NAME="$1"
LENGTH="$2" # in seconds
FPS="$3"

# optional: sleep during the x second acclimation period
# sleep x;

# start ffmpeg
# note here: the order of the arguments matters. Specifically, the framerate and video size arguments must be given before the -i or the line will throw an error
# this line was tested > 50 times with the logitech camera
ffmpeg -f avfoundation -video_size 1280x720 -framerate "$FPS" -i "Micro:none" -crf 28 -y -vcodec libx264 -t "$LENGTH" "$NAME"".avi"

# to find total frames: (double check this with other videos:
#ffprobe -select_streams v -show_streams test.avi 2>/dev/null | grep nb_frames | sed -e 's/nb_frames=//'

# wait for it to finish
wait

#start tracking
echo "tracking ${NAME}"
python realTimeTrackerShort.py -i ${NAME}.avi -n ${NAME} -f ${FPS} >> "$NAME""_log.txt"
cat "$NAME""_log.txt" | grep "part 2" -A 5
cat "$NAME""_log.txt" | grep "part 3" -A 5
tail -20 "$NAME""_log.txt"
