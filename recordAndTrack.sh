echo $0
# read in arguments
NAME="$1"
LENGTH="$2" # in seconds
FPS="$3"

# optional: sleep during acclimation period
# sleep 600

# start ffmpeg
ffmpeg -f avfoundation -i "Microsoft:none" -q 1 -r ${FPS} -t ${LENGTH} -vf "drawtext=fontfile=/Library/Fonts/Arial.ttf: text='%{localtime}': x=10: y=10: fontcolor=white: fontsize=30: box=1: boxcolor=0x00000000@1" -vf fps="fps=${FPS}" -vcodec libx264 -y ${NAME}.mp4

# wait for it to finish 
wait
# or try sleep 60

# start tracking
echo "tracking ${NAME}"
python realTimeTracker.py -i ${NAME}.mp4 -n ${NAME} -f ${FPS}