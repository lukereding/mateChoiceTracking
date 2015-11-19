# mateChoiceTracking

I'm using this repo to keep track of all the code I run for analzying position data from mate choice trials in fish.

### some general explanations about these scripts:
* Record trial overhead with webcam using ffmpeg. Then start tracking the fish immediately after the trial finishes. OpenCV is too slow at writing frames to a video file for it to make sense to do these two tasks at the same time. Run `bash -x recordAndTrack.sh name_of_trial 1260 10` to record a video called *name_of_trial.avi*. In this case, the video will be 1260 seconds long, or 21 minutes, and will have a framerate of 10. This script simply calls ffmpeg to record and save an avi video file, then calls `realTimeTrackerShort.py` (see below), putting all the arguments nicely in place. It saves standard out of this python script to a log file and spits out some association time stats to the screen when it's finished running.
* Running the above line saves a bunch of files to the local directory:
  * a log file (named with whatever name you passed above but appended with `_log.txt`)
  * a csv file with positions of the fish. If the fish was not found, the x and y values are listed as NA
  * a txt file with the list of punative association zones, one line for each frame
  * a jpg of the tank without a fish in it (it's basically a long-exposure photograph) and the same photo but with an rectangle showing where the computer determined the bounds of the tank were
* If for whatever reason you need to re-run the tracking script on all the .avi files in a directory, perhaps because you've made a small change to the code, run `bash run_tracking_script_on_all_avi_files.sh`
* Once you've run some trials and want to collect all the relavant data together in a csv file to import into R, use `bash -x make_csv.sh`. It'll output a file in the local directory called `out.csv` that contains a bunch of quantities of interest. This script just looks into all the log files that were created from capturing STDOUT from the tracking script and pulls out the bits of information you care about.
* If you need to make stimulus videos to use for mate choice studies, head over to the `making_animations` folder. Choose the shell script that best suits your purpose. The idea idea here is to add four videos to this folder (assuming you've locally cloned this repo): one that shows the first stimulus going from left to right, a second that shows the first stimulus going from right to left, and similar videos for the second stimulus. You pass the names of the videos as arguments to the script and it'll run a bunch of ffmpeg commands needed to turn them into video you can actually use in your trials. See the comment lines of the shell scripts for more specific instructions.

### some things to note:
* realTimeTracker.py does not actually track in real time.
  * `realTimeTracker.py` is optimized for 20 minute trials where the order or stimuli presentation is: background (5 min), stimuli (5 min), background (5 min), stimuli (5min).
  * `realTimeTrackerShort.py` is optimized for 21 minutes videos where the order of presentation is: background (5 min), stimuli (5 min), background (1 min), stimuli (5 min), background (5 min).
  * as written now, `recordAndTrack.sh` uses `realTimeTrackerShort.py`


### quick explanation of `realTimeTrackerShort.py`:
* The basic idea of the script:
  * Find out what the tank looks like without the fish in it. It uses this image as a reference for image subtraction. This image gets saved as a jpg for reference / error checking.
  * Find out where the bounds of the tank are. The script finds the biggest white blob (the gravel) and draws a rectangle around it. Nothing outside this rectangle will be tracked.
  * The tracker divides the tank up into thirds.
  * The tracker pulls each frame from the video file and subtracts it from the reference frame. Dark fish on a light background leave a characteristic signature. The tracker identifies groups of pixels that confirm to this signature, then filters these to identify the blob of pixels that is mostly likely the fish.
  * The script saves a list of the side of the tank the fish was on in each frame, as well as the tracking coordinates.
  * Any other information you could possibly want about the trial, the bounds of the tank, etc., are in the log file. You could use some really simply `grep` commands to pull out any information you want.
  *

### to make videos to present to fish
Best workflow:
+ clone this repo.
+ cd into this directory
+ add the following ingredients:
    + four animations. If you're have animations called A.avi and B.avi, you need A_flipped.avi and B_flipped.avi as well where the background in flipped
    + photo of whatever background you're using, of the same dimensions as the video
    + countdown
+ make this script executable with chmod +x makingVideosForMateChoiceExperiments.sh
+ bash +x makingVideosForMateChoiceExperiments.sh A B # for videos named A.avi, B.avi, A_flipped.avi, B_flipped.avi

### `ethogram.R`
I've found that I often want a quick and dirty way to visualize what a female is doing over time in the tank. Plotting the raw tracking data is too noisy and busy to be able to extract some meaning from it. `ethogram.R` takes the .txt file of sides occupied in each frame of a video (this is an output from `realTimeTrackerShort.py`) and makes a handy representation of which side of the tank the fish occupied throughout the trial.

The plot is broken up into five rows. Each row corresponds to one meaningful part of the trial. Colors represent different parts of the tank. `stim` refers to one type of male animation; as written now, it doesn't identify which male this is.

![ethogram](https://github.com/lukereding/mateChoiceTracking/raw/master/plotting/ethogram_example.png)
