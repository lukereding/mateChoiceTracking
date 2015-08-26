# mateChoiceTracking

I'm using this repo to keep track of all the code I run for analzying position data from mate choice trials in fish. 

The scototaxis tracking script is very similar to the general tracking script but there are some key differences. The histories directory contains specific examples of code I've used in the past to (1) slice the videos up and (2) run the tracking script on these videos.

## General workflow:
* Record trial overhead with webcam. Save as mp4 or avi. I've been using **<http://www.ispyconnect.com/>** for this.
* Convert all videos to the same format if they are in different formats or sizes.
* Cut video into different parts corresponding to different parts of the trial. I've been using the instructions in **unixCommands.txt** for this. It batch processes a bunch of **ffmpeg** commands.
* Analyze the videos using **differenceImageGravel.py**

## In development
**realTimeTracker.py** has a few aims:
* track fish in mate choice tank in real time
* save videos from each trial
* have the experimenter record the bounds of the fish tank prior to start of the experiment
* have the tracker record association time in real time
* have the program output error messages / let the experimenter know if there were problems with the tracker 
or if the fish needs to be re-tested
