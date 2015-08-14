# 14 August 2015
# explicit list of commands used for dividing mate choice videos up into different splices
# original n = 24 control trials for animations

mkdir coding
cd coding

# make a list of the videos for large vs bkg
find "/Volumes/LPRLABBKP/largeMaleVsBackground" | grep ".mp4" > listOfVideos
cat listOfVideos # looks right

mkdir largeMaleVsBackgroundVideosSpliced
cd largeMaleVsBackgroundVideosSpliced
pwd #/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/largeMaleVsBackgroundVideosSpliced
cd ..
cd coding

#### first step: just make sure all the videos have the same codec, etc
# do a sed replacement to insert the ffmpeg command
cat listOfVideos | sed 's,^\(.*\)\(/[A-Za-z].*_[A-Za-z].*\).mp4,ffmpeg -i \1\2.mp4 -vcodec libx264 -y /Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/largeMaleVsBackgroundVideosSpliced\2.mp4,' > remakeVids
head -1 remakeVids 
chmod +x remakeVids
./remakeVids

pwd #/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/coding
#### second step: splice each video up into four videos, each 5 minutes long
find "/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/largeMaleVsBackgroundVideosSpliced"  | grep ".mp4" | sed 's,\(/[A-Za-z].*_.*\).mp4,ffmpeg -ss 300 -i \1.mp4 -t 300 -vcodec libx264 \1_mateChoice1.mp4,' > mateChoice1
find "/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/largeMaleVsBackgroundVideosSpliced"  | grep ".mp4" | sed 's,\(/[A-Za-z].*_.*\).mp4,ffmpeg -ss 900 -i \1.mp4 -t 300 -vcodec libx264 \1_mateChoice2.mp4,' > mateChoice2
find "/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/largeMaleVsBackgroundVideosSpliced"  | grep ".mp4" | sed 's,\(/[A-Za-z].*_.*\).mp4,ffmpeg -ss 0 -i \1.mp4 -t 300 -vcodec libx264 \1_backgrounds1.mp4,' > backgrounds1
find "/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/largeMaleVsBackgroundVideosSpliced"  | grep ".mp4" | sed 's,\(/[A-Za-z].*_.*\).mp4,ffmpeg -ss 600 -i \1.mp4 -t 300 -vcodec libx264 \1_backgrounds2.mp4,' > backgrounds2

cat mateChoice1 mateChoice2 backgrounds1 backgrounds2 > allSplicing

wc -l allSplicing # 96 # 24*4 = 96 checks out

chmod +x allSplicing
./allSplicing

pwd #/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/coding
#### running the tracking code
find "/Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/largeMaleVsBackgroundVideosSpliced" | grep "_.*[12].mp4" > listOfVideos

# note that mateChoiceTracking was cloned from github
cat listOfVideos | sed 's,^\(.*\),python /Users/lukereding/Documents/mateChoiceTracking/differenceImageGravel.py -i \1,' > track
chmod +x track
caffeinate -i /Users/lukereding/Desktop/controlExperimentsAnimationsJulyAugust/coding/track
