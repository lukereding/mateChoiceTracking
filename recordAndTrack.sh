echo $0
# read in arguments
NAME="$1"
LENGTH="$2" # in seconds
FPS="$3"

# optional: sleep during the 10 minute acclimation period
sleep 600;

# start ffmpeg
ffmpeg -f avfoundation -i "Microsoft:none" -q 25 -t "$LENGTH" -vf fps="${FPS}" -vcodec libx264 -y "$NAME"".avi"


# wait for it to finish 
wait

# start tracking
echo "tracking ${NAME}"
python realTimeTracker.py -i ${NAME}.avi -n ${NAME} -f ${FPS}