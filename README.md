# mateChoiceTracking

I'm using this repo to keep track of all the code I run for analzying position data from mate choice trials in fish. 

## General workflow:
* Record trial overhead with webcam using ffmpeg. Then start tracking the fish immediately after the trial finishes. OpenCV is too slow at writing frames to a video file for it to make sense to do these two tasks at the same time. Run `bash -x recordAndTrack.sh name_of_trial 1260 10` to record a video called *name_of_trial.avi*. In this case, the video will be 1260 seconds long, or 21 minutes, and will have a framerate of 10.
* Running the above line saves a bunch of files to the local directory:
  * a log file (named with whatever name you passed above but appended with `_log.txt`)
  * a csv file with positions of the fish. If the fish was not found, the x and y values are listed as NA
  * a txt file with the list of punative association zones, one line for each frame
  * a jpg of the tank without a fish in it (it's basically a long-exposure photograph) and the same photo but with an rectangle showing where the computer determined the bounds of the tank were
* If for whatever reason you need to re-run the tracking script on all the .avi files in a directory, perhaps because you've made a small change to the code, run `bash run_tracking_script_on_all_avi_files.sh`
* Once you've run some trials and want to collect all the relavant data together in a csv file to import into R, use `bash -x make_csv.sh`. It'll output a file in the local directory called `out.csv` that contains a bunch of quantities of interest. This script just looks into all the log files that were created from capturing STDOUT from the tracking script and pulls out the bits of information you care about. 

### things to note:
* realTimeTracker.py does not actually track in real time. 
  * `realTimeTracker.py` is optimized for 20 minute trials where the order or stimuli presentation is: background (5 min), stimuli (5 min), background (5 min), stimuli (5min). 
  * `realTimeTrackerShort.py` is optimized for 21 minutes videos where the order of presentation is: background (5 min), stimuli (5 min), background (1 min), stimuli (5 min), background (5 min).
  * as written now, `recordAndTrack.sh` uses `realTimeTrackerShort.py`
