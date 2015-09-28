echo $0
# read in arguments
NAME="$1"
LENGTH="$2" # in seconds
FPS="$3"

# optional: sleep during the 10 minute acclimation period
sleep 5;

# start ffmpeg
# see https://trac.ffmpeg.org/wiki/EncodingForStreamingSites for explanations of some of the arguments
# I'm using ffmpeg 2.6.3 install via brew (need to do a brew log ffmpeg and find specific commit)
# my Mac is running OSX Yosemite ver. 10.10.5, 2.5 GHz processer, 8 GB RAM
# to get this to work on something other than ffmpeg v 2.6.3, pass the -i argument after the size and framerate options # this works for Ian, but not for me

# this line was tested > 50 times with the logitech camera
ffmpeg -f avfoundation -video_size 1280x720 -framerate "$FPS" -i "Micro:none" -crf 32 -vcodec libx264 -y -t "$LENGTH" "$NAME"".avi"

# to find total frames: (double check this with other videos:
#ffprobe -select_streams v -show_streams test.avi 2>/dev/null | grep nb_frames | sed -e 's/nb_frames=//'

# wait for it to finish 
wait

#start tracking
echo "tracking ${NAME}"
python realTimeTracker.py -i ${NAME}.mpg -n ${NAME} -f ${FPS} >> "$NAME""_log.txt"
cat "$NAME""_log.txt" | grep "part 2" -A 5
cat "$NAME""_log.txt" | grep "part 4" -A 5 
tail -16 "$NAME""_log.txt"
