echo $0
# read in arguments
NAME="$1"
LENGTH="$2" # in seconds
FPS="$3"

# optional: sleep during the 10 minute acclimation period
sleep 598;

which ffmpeg

# start ffmpeg
# see https://trac.ffmpeg.org/wiki/EncodingForStreamingSites for explanations of some of the arguments
ffmpeg -f avfoundation -i "Microsoft:none" -preset superfast -q 30 -crf 30 -maxrate 3000k -bufsize 800k -r "$FPS" -framerate "$FPS" -t "$LENGTH" -vcodec libx264 -y "$NAME"".avi"


# wait for it to finish 
wait

# start tracking
echo "tracking ${NAME}"
python realTimeTracker.py -i ${NAME}.avi -n ${NAME} -f ${FPS} >> "$NAME""_log.txt"
cat "$NAME""_log.txt" | grep "part 2" -A 5
cat "$NAME""_log.txt" | grep "part 4" -A 5 
tail -16 "$NAME""_log.txt"